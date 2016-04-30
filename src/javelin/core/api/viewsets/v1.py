import re
import time
import uuid
import datetime

import django_filters
from django_twilio.client import twilio_client
from twilio import TwilioRestException

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.core.mail import send_mail

from django.core.exceptions import PermissionDenied

from rest_framework import generics
from rest_framework import permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status, viewsets, ISO_8601
from rest_framework.decorators import detail_route, list_route
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from ..serializers.v1 import (UserSerializer, GroupSerializer,
                              AgencySerializer, AlertSerializer,
                              AlertLocationSerializer,
                              ChatMessageSerializer,
                              MassAlertSerializer,
                              UserProfileSerializer,
                              SocialCrimeReportSerializer,
                              EntourageMemberSerializer,
                              UnauthorizedEntourageMemberSerializer,
                              RegionSerializer,
                              DispatchCenterSerializer,
                              PeriodSerializer,
                              ClosedDateSerializer,
                              StaticDeviceSerializer, ThemeSerializer,
                              EntourageSessionSerializer, TrackingLocationSerializer,
                              NamedLocationSerializer,
                              UserNoLocationEntourageMemberSerializer, UserTrackingEntourageMemberSerializer,
                              UserAlwaysVisibleEntourageMemberSerializer, PostUserSerializer,
                              TrackingLocationFullSerializer, EntourageSessionPostSerializer,
                              UserNotificationSerializer)

from ....core.aws.dynamodb import DynamoDBManager
from ....core.aws.sns import SNSManager
from ....core.filters import IsoDateTimeFilter
from ....core.models import (Agency, Alert, AlertLocation,
                             ChatMessage, MassAlert, UserProfile, EntourageMember,
                             SocialCrimeReport, Region,
                             DispatchCenter, Period, AgencyUser,
                             ClosedDate, StaticDevice, Theme,
                             EntourageSession, TrackingLocation, NamedLocation, UserNotification)

from ....core.utils import get_agency_from_unknown

from ....core.tasks import (create_user_device_endpoint, publish_to_agency_topic,
                            notify_new_chat_message_available, notify_crime_report_marked_viewed,
                            notify_alert_completed, new_static_alert)

User = get_user_model()


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has a `user` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `user`.
        return obj.user == request.user


class DeviceMakerOnly(permissions.BasePermission):
    """
    Only allows Device Maker group to view or edit.
    """

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        permitted_groups = [Group.objects.get(name='Device Maker'), ]
        if request.user.is_authenticated():
            if bool(request.user.groups.filter(name__in=permitted_groups)) | request.user.is_superuser:
                return True
            return False
        return False


class IsRequestUserOrDispatcher(permissions.BasePermission):
    """
    Object-level User account permission to only allow the user or dispatchers to access
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.

        if request.method in permissions.SAFE_METHODS:
            if request.user.is_authenticated():
                if request.user.groups.filter(name='Dispatchers').count() != 0:
                    return True

        return bool(obj == request.user) | request.user.is_superuser


class EntourageMemberViewSet(viewsets.ModelViewSet):
    permission_classes = (IsOwnerOrReadOnly, IsAuthenticated,)
    queryset = EntourageMember.objects.select_related('user').all()
    model = EntourageMember
    serializer_class = EntourageMemberSerializer
    filter_fields = ('user',)

    def get_queryset(self):
        if not self.request.user.is_staff and not self.request.user.is_superuser:
            return EntourageMember.objects.filter(user=self.request.user)

        return EntourageMember.objects.select_related('user').all()


class UserViewSet(viewsets.ModelViewSet):
    model = User
    filter_fields = ('agency',)
    permission_classes = (IsRequestUserOrDispatcher, IsAuthenticated,)
    serializer_class = UserSerializer

    def get_serializer_class(self):

        if self.request.method == 'GET' and not hasattr(self, 'response'):
            return UserSerializer
        elif self.request.method in ('POST', 'PUT', 'PATCH') \
                and not hasattr(self, 'response'):
            return PostUserSerializer

        return UserSerializer

    def get_queryset(self):

        if self.request.user.is_staff or self.request.user.is_superuser:
            qs = User.objects.select_related('agency').prefetch_related('groups', 'entourage_members').all()
        else:
            qs = User.objects.select_related('agency').prefetch_related('groups', 'entourage_members') \
                .filter(pk=self.request.user.pk)
        return qs

    @detail_route(methods=['post', ])
    def message_entourage(self, request, pk=None):
        message = request.DATA.get('message', None)
        subject = request.DATA.get('subject', None)
        if message:
            user = self.get_object()
            entourage_members = user.entourage_members.all()
            errors = []
            for em in entourage_members:
                if em.phone_number:
                    try:
                        resp = twilio_client.messages.create( \
                            to=em.phone_number,
                            from_=settings.TWILIO_SMS_VERIFICATION_FROM_NUMBER,
                            body=message)
                        if resp.status == 'failed':
                            errors.append( \
                                {"Entourage Member %d" % \
                                 em.id: 'Error sending SMS Verification',
                                 "id": em.id})
                    except TwilioRestException, e:
                        if e.code and e.code == 21211:
                            errors.append( \
                                {"Entourage Member %d" % \
                                 em.id: 'Invalid phone number',
                                 "id": em.id})
                elif em.email_address:
                    if not subject:
                        subject = "A message from TapShield"
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                              [em.email_address], fail_silently=True)
        else:
            return Response( \
                {'message': 'message is a required parameter.'},
                status=status.HTTP_400_BAD_REQUEST)
        if errors:
            return Response({'message': 'Partial Success',
                             'errors': errors})
        else:
            return Response({'message': 'Success'})

    @detail_route(methods=['post'])
    def update_required_info(self, request, pk=None):
        user = self.get_object()
        valid_keys = ['agency', 'phone_number', 'disarm_code',
                      'first_name', 'last_name']
        info_dict = request.POST.copy()
        if 'agency' in info_dict:
            try:
                info_dict['agency'] = \
                    Agency.objects.get(pk=info_dict['agency'])
            except Agency.DoesNotExist:
                return Response({'message': 'No matching agency found.'},
                                status=status.HTTP_400_BAD_REQUEST)
        for k, v in info_dict.items():
            if not k in valid_keys:
                continue
            if hasattr(user, k):
                setattr(user, k, v)
        user.save()
        serializer = UserSerializer(user, context={'request': request})
        if serializer.data:
            return Response(serializer.data)
        else:
            return Response( \
                {'message': 'There was an error with the values provided.'},
                status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def update_device_token(self, request, pk=None):
        """
        Set the device token for the specified user.

        deviceToken -- The push notification token to store
        deviceType -- iOS, Android, etc. Use 'I' for iOS, 'A' for Android.
        """
        if request.user.is_superuser or request.user.pk == int(pk):
            device_token = request.DATA.get('deviceToken', None)
            device_type = request.DATA.get('deviceType', None)
            if not device_token:
                return Response( \
                    {'message': 'deviceToken is a required parameter'},
                    status=status.HTTP_400_BAD_REQUEST)
            elif not device_type:
                return Response( \
                    {'message': 'deviceType is a required parameter'},
                    status=status.HTTP_400_BAD_REQUEST)
            else:
                try:
                    user = self.get_object()
                    user.device_token = device_token
                    user.device_type = device_type
                    user.save()
                    create_user_device_endpoint.delay(user.pk,
                                                      user.device_type,
                                                      user.device_token)
                    return Response({'message': 'Success'})
                except User.DoesNotExist:
                    return Response({'message': 'user not found'},
                                    status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Not found.'},
                        status=status.HTTP_404_NOT_FOUND)

    @detail_route(methods=['post'])
    def send_sms_verification_code(self, request, pk=None):
        if request.user.is_superuser or request.user.pk == int(pk):
            phone_number = request.DATA.get('phone_number', None)
            if not phone_number:
                return Response( \
                    {'message': 'phone_number is a required parameter'},
                    status=status.HTTP_400_BAD_REQUEST)
            try:
                phone_number = re.sub("\D", "", phone_number)
                text_number = "+1%s" % phone_number

                if len(phone_number) > 10:
                    text_number = "+%s" % phone_number

                user = self.get_object()
                user.phone_number_verification_code = None
                user.save()
                resp = twilio_client.messages.create( \
                    to=text_number,
                    from_=settings.TWILIO_SMS_VERIFICATION_FROM_NUMBER,
                    body="Your TapShield verification code is: %s" \
                         % user.phone_number_verification_code)
                if not resp.status == 'failed':
                    return Response({'message': 'Success'})
                else:
                    return Response( \
                        {'message': 'Error sending SMS Verification'},
                        status=status.HTTP_400_BAD_REQUEST)
            except TwilioRestException, e:
                if e.code and e.code == 21211:
                    return Response({'message': 'Invalid phone number'},
                                    status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Not found.'},
                        status=status.HTTP_404_NOT_FOUND)

    @detail_route(methods=['post'])
    def check_sms_verification_code(self, request, pk=None):
        """
        Checks the provided code against the code sent to the user
        via SMS for phone number verification.

        code -- The code to check
        """
        if request.user.is_superuser or request.user.pk == int(pk):
            code = request.DATA.get('code', None)
            if not code:
                return Response( \
                    {'message': 'code is a required parameter'},
                    status=status.HTTP_400_BAD_REQUEST)
            try:
                code = int(code.strip())
            except ValueError:
                return Response( \
                    {'message': 'Incorrect type for code'},
                    status=status.HTTP_400_BAD_REQUEST)
            user = self.get_object()
            if code == user.phone_number_verification_code:
                user.phone_number_verified = True
                user.save()
                return Response( \
                    {'message': 'OK'},
                    status=status.HTTP_200_OK)
            else:
                return Response( \
                    {'message': 'Incorrect code'},
                    status=status.HTTP_400_BAD_REQUEST)

    @detail_route(['get'])
    def matched_entourage_users(self, request, pk=None):

        user = self.get_object()

        if not user == request.user:
            matching_members = EntourageMember.objects.filter(matched_user=user).values('user')
            return Response(UserNoLocationEntourageMemberSerializer(matching_members,
                                                                    many=True,
                                                                    context={'request': request}).data,
                            status=status.HTTP_200_OK)

        user.match_with_entourage_members()

        always_visible_users_id = EntourageMember.objects.filter(matched_user=user,
                                                                 always_visible=True).values('user_id')
        tracking_users_id = EntourageMember.objects.filter(matched_user=user,
                                                           always_visible=False,
                                                           track_route=True).values('user_id')
        no_tracking_users_id = EntourageMember.objects.filter(matched_user=user,
                                                              always_visible=False,
                                                              track_route=False).values('user_id')

        always_visible_users = User.objects.filter(id__in=always_visible_users_id)
        tracking_users = User.objects.filter(id__in=tracking_users_id)
        no_tracking_users = User.objects.filter(id__in=no_tracking_users_id)

        serialized_always = UserAlwaysVisibleEntourageMemberSerializer(always_visible_users, many=True,
                                                                       context={'request': request})
        serialized_tracking = UserTrackingEntourageMemberSerializer(tracking_users, many=True,
                                                                    context={'request': request})
        serialized_no_tracking = UserNoLocationEntourageMemberSerializer(no_tracking_users, many=True,
                                                                         context={'request': request})

        serialized_data = serialized_always.data + serialized_tracking.data + serialized_no_tracking.data

        return Response(serialized_data,
                        status=status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def locations(self, request, pk=None):

        request_data = request.DATA

        user = self.get_object()

        active_sessions = EntourageSession.tracking.filter(user=user)
        active_alert = Alert.active.filter(agency_user=user)

        for location_dict in request_data:

            accuracy = location_dict['accuracy']

            if accuracy < 500:
                if active_sessions:
                    session = active_sessions[0]
                    new_location = TrackingLocation(entourage_session=session,
                                                    accuracy=accuracy,
                                                    altitude=location_dict['altitude'],
                                                    latitude=location_dict['latitude'],
                                                    longitude=location_dict['longitude'])
                    new_location.save()

                if active_alert:
                    alert = active_alert[0]
                    new_location = AlertLocation(alert=alert,
                                                 accuracy=accuracy,
                                                 altitude=location_dict['altitude'],
                                                 latitude=location_dict['latitude'],
                                                 longitude=location_dict['longitude'],
                                                 floor_level=location_dict['floor_level'])
                    new_location.save()

                if location_dict == request_data[-1]:
                    user.__dict__.update(location_dict)
                    user.save()

        return Response({'message': "Updated"},
                        status=status.HTTP_201_CREATED)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class SocialCrimeReportModifiedSinceFilterBackend(django_filters.FilterSet):
    modified_since = IsoDateTimeFilter(name="last_modified",
                                       lookup_type='gt',
                                       input_formats=(ISO_8601,
                                                      '%m/%d/%Y %H:%M:%S'))

    class Meta:
        model = SocialCrimeReport


class SocialCrimeReportViewSet(viewsets.ModelViewSet):
    model = SocialCrimeReport
    serializer_class = SocialCrimeReportSerializer
    filter_class = SocialCrimeReportModifiedSinceFilterBackend

    def get_queryset(self):

        qs = SocialCrimeReport.objects.all()
        latitude = self.request.query_params.get('latitude', None)
        longitude = self.request.query_params.get('longitude', None)
        distance_within = \
            self.request.query_params.get('distance_within', None)
        if (latitude and longitude) and distance_within:
            point = Point(float(longitude), float(latitude))
            dwithin = float(distance_within)
            qs = qs.filter(report_point__dwithin=(point, D(mi=dwithin))).distance(point).order_by('distance')
        elif latitude or longitude or distance_within:
            # We got one or more values but not all we need, so return none
            qs = SocialCrimeReport.objects.none()
        return qs

    @detail_route(methods=['post'])
    def mark_viewed(self, request, pk=None):

        if not request.user.is_superuser:
            if request.user.groups.filter(name='Dispatchers').count() == 0:
                raise PermissionDenied

        report = self.get_object()
        if report.viewed_by:
            return Response({'message': 'Report was already marked viewed'},
                            status=status.HTTP_400_BAD_REQUEST)

        report.viewed_by = request.user
        report.viewed_time = datetime.datetime.now()
        report.save()

        message = "%s dispatcher %s viewed your report. Thank you!" \
                  % (request.user.agency.name, request.user.first_name)

        reporter = report.reporter
        notify_crime_report_marked_viewed.delay(
            message, report.id,
            reporter.device_type,
            reporter.device_endpoint_arn)

        return Response(SocialCrimeReportSerializer(instance=report, context={'request': request}).data,
                        status=status.HTTP_200_OK)


class AgencyViewSet(viewsets.ModelViewSet):
    model = Agency
    serializer_class = AgencySerializer
    filter_backends = (SearchFilter,)
    search_fields = ('domain',)

    def get_queryset(self):
        qs = Agency.objects.all()
        latitude = self.request.query_params.get('latitude', None)
        longitude = self.request.query_params.get('longitude', None)
        distance_within = \
            self.request.query_params.get('distance_within', None)
        if (latitude and longitude) and distance_within:
            point = Point(float(longitude), float(latitude))
            dwithin = float(distance_within)
            qs = Agency.geo.select_related('agency_point_of_contact') \
                .filter(agency_center_point__dwithin=(point,
                                                      D(mi=dwithin))) \
                .distance(point).order_by('distance')
        elif latitude or longitude or distance_within:
            # We got one or more values but not all we need, so return none
            qs = Agency.objects.none()

        if self.request.user.is_staff:
            return qs

        return qs.exclude(hidden=True)

    @detail_route(methods=['post'])
    def send_mass_alert(self, request, pk=None):
        """
        Sends a message to all devices subscribed to the agency's SNS topic
        endpoint.

        message -- The message to send
        """
        message = request.DATA.get('message', None)
        if not message:
            return Response({'message': 'message is a required parameter'},
                            status=status.HTTP_400_BAD_REQUEST)

        sns = SNSManager()
        agency = self.get_object()
        publish_to_agency_topic.delay(agency.sns_primary_topic_arn, message)
        mass_alert = MassAlert(agency_dispatcher=request.user,
                               agency=agency,
                               message=message)
        mass_alert.save()
        return Response({'message': 'Ok'},
                        status=status.HTTP_200_OK)


class AlertsModifiedSinceFilterBackend(django_filters.FilterSet):
    last_alert_received = django_filters.NumberFilter(name="id",
                                                      lookup_type='gt')
    modified_since = IsoDateTimeFilter(name="last_modified",
                                       lookup_type='gt',
                                       input_formats=(ISO_8601,
                                                      '%m/%d/%Y %H:%M:%S'))

    class Meta:
        model = Alert


class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.select_related('agency', 'agency_user', 'agency_dispatcher').prefetch_related(
        'locations').all()
    serializer_class = AlertSerializer
    filter_fields = ('agency', 'agency_user', 'agency_dispatcher',
                     'status', 'initiated_by',)
    filter_class = AlertsModifiedSinceFilterBackend

    @detail_route(methods=['post'])
    def complete(self, request, pk=None):
        """
        Set a alert completed.
        This will send a completion message to the user and disarm
        """
        alert = self.get_object()

        if not alert.agency_dispatcher == request.user:
            raise PermissionDenied

        alert.status = 'C'
        alert.save()
        serialized = AlertSerializer(alert, context={'request': request})

        if not alert.agency_user:
            return Response(serialized.data)

        message = "Dispatcher has ended this chat session"
        message_id = str(uuid.uuid1())
        dynamo_db = DynamoDBManager()
        dynamo_db.save_item_to_table(settings.DYNAMO_DB_CHAT_MESSAGES_TABLE,
                                     {'alert_id': int(pk),
                                      'sender_id': int(2),
                                      'message': "Dispatcher has ended this chat session",
                                      'timestamp': time.time(),
                                      'message_id': message_id})

        push_notification_message = alert.agency.alert_completed_message
        push_notification_message = push_notification_message.replace("<first_name>", request.user.first_name)

        if alert.initiated_by == "C":
            push_notification_message = "Dispatcher has ended your chat session"

        if not request.user.id == alert.agency_user.id:
            user = alert.agency_user
            notify_alert_completed.delay(push_notification_message, serialized.data['url'], user.device_type,
                                         user.device_endpoint_arn)

        return Response(serialized.data)

    @detail_route(methods=['post'])
    def disarm(self, request, pk=None):
        """
        Set a disarmed time on the alert. This indicates that the user wishes
        to cancel the alert.
        """
        alert = self.get_object()
        alert.disarm()
        serialized = AlertSerializer(alert, context={'request': request})
        return Response(serialized.data)

    @detail_route(methods=['post'])
    def send_message(self, request, pk=None):
        """
        Sends a chat message to DynamoDB, tied to the specified alert's PK.
        The message will automatically receive the appropriate sender PK,
        UUID, and Unix timestamp

        message -- The message to send
        """
        message = request.DATA.get('message', None)
        if message:
            message_id = str(uuid.uuid1())
            dynamo_db = DynamoDBManager()
            dynamo_db.save_item_to_table( \
                settings.DYNAMO_DB_CHAT_MESSAGES_TABLE,
                {'alert_id': int(pk), 'sender_id': request.user.id,
                 'message': message, 'timestamp': time.time(),
                 'message_id': message_id})
            alert = self.get_object()
            if not request.user.id == alert.agency_user.id:
                user = alert.agency_user
                notify_new_chat_message_available.delay( \
                    message, message_id,
                    user.device_type,
                    user.device_endpoint_arn)
            return Response({'message': 'Chat received'})
        else:
            return Response( \
                {'message': "message and sender are required parameters"},
                status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['get'])
    def messages(self, request, pk=None):
        """
        Get all messages for the given alert.
        """
        dynamo_db = DynamoDBManager()
        messages = dynamo_db.get_messages_for_alert(pk)
        return Response(messages)

    @detail_route(methods=['get'])
    def messages_since(self, request, pk=None):
        """
        Get all messages for the given alert since the provided Unix timestamp.

        timestamp -- Get messages since this Unix timestamp.
        """
        timestamp = request.GET.get('timestamp', None)
        if not timestamp:
            return Response({'message': 'timestamp is a required parameter'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            dynamo_db = DynamoDBManager()
            messages = dynamo_db.get_messages_for_alert_since_time(pk,
                                                                   timestamp)
            return Response(messages)
        except ValueError:
            return Response( \
                {'message': "timestamp must be an Unix timestamp"},
                status=status.HTTP_400_BAD_REQUEST)


class AlertLocationViewSet(viewsets.ModelViewSet):
    queryset = AlertLocation.objects.select_related('alert').all()
    serializer_class = AlertLocationSerializer
    filter_fields = ('alert',)

    def create(self, request):

        active_alerts = Alert.active.filter(agency_user=request.user)

        serializer = self.get_serializer(data=request.DATA, files=request.FILES)

        if serializer.is_valid():
            self.pre_save(serializer.object)
            self.object = serializer.save(force_insert=True)
            self.post_save(self.object, created=True)
            headers = self.get_success_headers(serializer.data)

            if not active_alerts:
                return Response(serializer.data, status=status.HTTP_404_NOT_FOUND,
                                headers=headers)

            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.select_related().all()
    serializer_class = ChatMessageSerializer
    filter_fields = ('alert', 'sender', 'creation_date', 'last_modified',
                     'sender__agency',)


class MassAlertViewSet(viewsets.ModelViewSet):
    queryset = MassAlert.objects.select_related('agency').all()
    serializer_class = MassAlertSerializer
    filter_fields = ('agency', 'agency_dispatcher',)
    ordering = ('-creation_date',)


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.select_related().all()
    serializer_class = UserProfileSerializer
    filter_fields = ('user',)


class PeriodViewSet(viewsets.ModelViewSet):
    queryset = Period.objects.select_related('dispatch_center').all()
    serializer_class = PeriodSerializer
    filter_fields = ('dispatch_center',)


class ClosedDateViewSet(viewsets.ModelViewSet):
    queryset = ClosedDate.objects.select_related('dispatch_center').all()
    serializer_class = ClosedDateSerializer
    filter_fields = ('dispatch_center',)


class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.select_related('agency').all()
    serializer_class = RegionSerializer
    filter_fields = ('agency',)


class DispatchCenterViewSet(viewsets.ModelViewSet):
    queryset = DispatchCenter.objects.select_related('agency').all()
    serializer_class = DispatchCenterSerializer
    filter_fields = ('agency',)


class ThemeViewSet(viewsets.ModelViewSet):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer


class EntourageSessionViewSet(viewsets.ModelViewSet):
    queryset = EntourageSession.objects.all()
    serializer_class = EntourageSessionPostSerializer

    def get_serializer_class(self):

        if self.request.method == 'GET' and not hasattr(self, 'response'):
            return EntourageSessionSerializer
        elif self.request.method in ('POST', 'PUT', 'PATCH') \
                and not hasattr(self, 'response'):
            return EntourageSessionPostSerializer

        return EntourageSessionSerializer

    def create(self, request):

        active_sessions = EntourageSession.tracking.filter(user=request.user)
        if active_sessions:
            for session in active_sessions:
                session.status = "U"
                session.save()

        request_data = request.DATA.copy()
        request_data['user'] = UserSerializer(request.user, context={'request': request}).data['url']

        start_location_serialized = NamedLocationSerializer(data=request_data['start_location'],
                                                            context={'request': request})
        end_location_serialized = NamedLocationSerializer(data=request_data['end_location'],
                                                          context={'request': request})

        if not start_location_serialized.is_valid():
            return Response(start_location_serialized.errors, status=status.HTTP_400_BAD_REQUEST)

        if not end_location_serialized.is_valid():
            return Response(end_location_serialized.errors, status=status.HTTP_400_BAD_REQUEST)

        start_location_serialized.save()
        end_location_serialized.save()

        request_data['start_location'] = start_location_serialized.data['url']
        request_data['end_location'] = end_location_serialized.data['url']

        serializer = self.get_serializer(data=request_data, files=request.FILES)

        if serializer.is_valid():
            self.pre_save(serializer.object)
            self.object = serializer.save(force_insert=True)
            self.post_save(self.object, created=True)
            headers = self.get_success_headers(serializer.data)

            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def arrived(self, request, pk=None):

        """
        arrived at location
        """
        session = self.get_object()
        message = session.arrived()
        serialized = EntourageSessionPostSerializer(session, context={'request': request})
        if not message:
            message = serialized.data
        return Response(message,
                        status=status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def cancel(self, request, pk=None):

        """
        Cancelled tracking of session
        """
        session = self.get_object()
        session.cancel()
        return Response({"message": "Cancelled"},
                        status=status.HTTP_200_OK)


class TrackingLocationViewSet(viewsets.ModelViewSet):
    queryset = TrackingLocation.objects.all()
    serializer_class = TrackingLocationFullSerializer


class NamedLocationViewSet(viewsets.ModelViewSet):
    queryset = NamedLocation.objects.all()
    serializer_class = NamedLocationSerializer


class UserNotificationViewSet(viewsets.ModelViewSet):
    queryset = UserNotification.objects.all()
    serializer_class = UserNotificationSerializer

    def get_queryset(self):
        user = self.request.query_params.get('user', None)
        if self.request.user.is_superuser:
            if user:
                return UserNotification.objects.filter(user=user)
            return UserNotification.objects.all()
        return UserNotification.objects.filter(user=self.request.user)


class StaticDeviceViewSet(viewsets.ModelViewSet):
    permission_classes = (IsOwnerOrReadOnly, DeviceMakerOnly)
    queryset = StaticDevice.objects.all()
    serializer_class = StaticDeviceSerializer
    filter_fields = ('agency',)

    def create(self, request):

        request_data = request.DATA.copy()
        request_data['user'] = UserSerializer(request.user, context={'request': request}).data['url']
        agency_id = request_data.get('agency', None)

        agency = None
        if agency_id:
            agency = get_agency_from_unknown(agency_id)
        if agency:
            request_data['agency'] = AgencySerializer(agency, context={'request': request}).data['url']

        serializer = self.get_serializer(data=request_data, files=request.FILES, context={'request': request})

        if serializer.is_valid():

            self.pre_save(serializer.object)
            self.object = serializer.save(force_insert=True)
            self.post_save(self.object, created=True)

            if not self.object.agency:
                self.object.delete()
                return Response("Could not find agency or agency not provided", status=status.HTTP_400_BAD_REQUEST)

            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):

        mutable = request.DATA._mutable
        request.DATA._mutable = True
        request.DATA['user'] = UserSerializer(request.user, context={'request': request}).data['url']
        agency_id = request.DATA.get('agency', None)

        agency = None
        if agency_id:
            agency = get_agency_from_unknown(agency_id)
        if agency:
            request.DATA['agency'] = AgencySerializer(agency, context={'request': request}).data['url']
        else:
            request.DATA['agency'] = StaticDeviceSerializer(self, context={'request': request}).data['agency']

        request.DATA._mutable = mutable

        return super(StaticDeviceViewSet, self).update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):

        mutable = request.DATA._mutable
        request.DATA._mutable = True
        request.DATA['user'] = UserSerializer(request.user, context={'request': request}).data['url']
        agency_id = request.DATA.get('agency', None)

        agency = None
        if agency_id:
            agency = get_agency_from_unknown(agency_id)
        if agency:
            request.DATA['agency'] = AgencySerializer(agency, context={'request': request}).data['url']
        else:
            request.DATA['agency'] = StaticDeviceSerializer(self, context={'request': request}).data['agency']

        request.DATA._mutable = mutable

        return super(StaticDeviceViewSet, self).partial_update(request, *args, **kwargs)

        # @csrf_exempt
        # @detail_route(methods=['get'])
        # def alert(self, request, pk=None):
        #
        #     response = HttpResponse(content="Created")
        #     response.status_code = 201
        #     alert = new_static_alert(self.get_object())
        #     serializer = AlertSerializer(instance=alert)
        #
        #     headers = {}
        #     try:
        #         headers = {'Location': serializer.data[api_settings.URL_FIELD_NAME]}
        #     except (TypeError, KeyError):
        #         pass
        #     return Response(serializer.data, status=status.HTTP_201_CREATED,
        #                     headers=headers)


class StaticDeviceDetail(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    lookup_field = 'uuid'
    queryset = StaticDevice.objects.all()
    serializer_class = StaticDeviceSerializer
