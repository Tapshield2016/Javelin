import re
import time
import uuid

import django_filters
from django_twilio.client import twilio_client
from twilio import TwilioRestException

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.core.mail import send_mail

from rest_framework import status, viewsets, ISO_8601
from rest_framework.decorators import action
from rest_framework.filters import (DjangoFilterBackend, OrderingFilter,
                                    SearchFilter)
from rest_framework.response import Response

from core.api.serializers.v1 import (UserSerializer, GroupSerializer,
                                     AgencySerializer, AlertSerializer,
                                     AlertLocationSerializer,
                                     ChatMessageSerializer,
                                     MassAlertSerializer,
                                     UserProfileSerializer,
                                     SocialCrimeReportSerializer,
                                     EntourageMemberGETSerializer,
                                     EntourageMemberUpdateSerializer,
                                     UserUpdateSerializer,
                                     RegionSerializer,
                                     DispatchCenterSerializer,
                                     PeriodSerializer,
                                     ClosedDateSerializer)

from core.aws.dynamodb import DynamoDBManager
from core.aws.sns import SNSManager
from core.filters import IsoDateTimeFilter
from core.models import (Agency, Alert, AlertLocation,
                         ChatMessage, MassAlert, UserProfile,
                         ChatMessage, MassAlert, UserProfile, EntourageMember,
                         SocialCrimeReport,  Region,
                         DispatchCenter, Period,
                         ClosedDate)

from core.tasks import (create_user_device_endpoint, publish_to_agency_topic,
                        publish_to_device, notify_new_chat_message_available)

User = get_user_model()


class EntourageMemberViewSet(viewsets.ModelViewSet):
    queryset = EntourageMember.objects.select_related('user').all()
    model = EntourageMember
    filter_fields = ('user',)

    def get_serializer_class(self):
        if self.request.method == 'GET' and not hasattr(self, 'response'):
            return EntourageMemberGETSerializer
        elif self.request.method in ('POST', 'PUT', 'PATCH')\
                and not hasattr(self, 'response'):
            return EntourageMemberUpdateSerializer

        return EntourageMemberGETSerializer


class UserViewSet(viewsets.ModelViewSet):
    model = User
    filter_fields = ('agency',)

    def get_serializer_class(self):
        if self.request.method == 'GET' and not hasattr(self, 'response'):
            return UserSerializer
        elif self.request.method in ('POST', 'PUT', 'PATCH')\
                and not hasattr(self, 'response'):
            return UserUpdateSerializer

        return UserSerializer

    def get_queryset(self):
        qs = User.objects.select_related('agency')\
            .prefetch_related('groups', 'entourage_members').all()
        latitude = self.request.QUERY_PARAMS.get('latitude', None)
        longitude = self.request.QUERY_PARAMS.get('longitude', None)
        distance_within =\
            self.request.QUERY_PARAMS.get('distance_within', None)
        if (latitude and longitude) and distance_within:
            point = Point(float(longitude), float(latitude))
            dwithin = float(distance_within)
            qs = User.geo.select_related('agency')\
                .prefetch_related('groups', 'entourage_members')\
                .filter(last_reported_point__dwithin=(point, D(mi=dwithin)))\
                .distance(point).order_by('distance')
        elif latitude or longitude or distance_within:
            # We got one or more values but not all we need, so return none
            qs = User.objects.none()
        return qs

    @action(methods=['POST',])
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
                        resp = twilio_client.messages.create(\
                            to=em.phone_number,
                            from_=settings.TWILIO_SMS_VERIFICATION_FROM_NUMBER,
                            body=message)
                        if resp.status == 'failed':
                            errors.append(\
                                {"Entourage Member %d" %\
                                     em.id: 'Error sending SMS Verification',
                                 "id": em.id})
                    except TwilioRestException, e:
                        if e.code and e.code == 21211:
                            errors.append(\
                                {"Entourage Member %d" %\
                                     em.id: 'Invalid phone number',
                                 "id": em.id})
                elif em.email_address:
                    if not subject:
                        subject = "A message from TapShield"
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                              [em.email_address], fail_silently=True)
        else:
            return Response(\
                {'message': 'message is a required parameter.'},
                status=status.HTTP_400_BAD_REQUEST)
        if errors:
            return Response({'message': 'Partial Success',
                             'errors': errors})
        else:
            return Response({'message': 'Success'})

    @action(methods=['post',])
    def update_required_info(self, request, pk=None):
        user = self.get_object()
        valid_keys = ['agency', 'phone_number', 'disarm_code',
                      'first_name', 'last_name']
        info_dict = request.POST.copy()
        if 'agency' in info_dict:
            try:
                info_dict['agency'] =\
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
        serializer = UserSerializer(user)
        if serializer.data:
            return Response(serializer.data)
        else:
            return Response(\
                {'message': 'There was an error with the values provided.'},
                status=status.HTTP_400_BAD_REQUEST)

    @action()
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
                return Response(\
                    {'message': 'deviceToken is a required parameter'},
                    status=status.HTTP_400_BAD_REQUEST)
            elif not device_type:
                return Response(\
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

    @action()
    def send_sms_verification_code(self, request, pk=None):
        if request.user.is_superuser or request.user.pk == int(pk):
            phone_number = request.DATA.get('phone_number', None)
            if not phone_number:
                return Response(\
                    {'message': 'phone_number is a required parameter'},
                    status=status.HTTP_400_BAD_REQUEST)
            try:
                user = self.get_object()
                user.phone_number_verification_code = None
                user.save()
                resp = twilio_client.messages.create(\
                    to=phone_number,
                    from_=settings.TWILIO_SMS_VERIFICATION_FROM_NUMBER,
                    body="Your TapShield verification code is: %s"\
                        % user.phone_number_verification_code)
                if not resp.status == 'failed':
                    return Response({'message': 'Success'})
                else:
                    return Response(\
                        {'message': 'Error sending SMS Verification'},
                        status=status.HTTP_400_BAD_REQUEST)
            except TwilioRestException, e:
                if e.code and e.code == 21211:
                    return Response({'message': 'Invalid phone number'},
                                    status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Not found.'},
                         status=status.HTTP_404_NOT_FOUND)

    @action()
    def check_sms_verification_code(self, request, pk=None):
        """
        Checks the provided code against the code sent to the user
        via SMS for phone number verification.

        code -- The code to check
        """
        if request.user.is_superuser or request.user.pk == int(pk):
            code = request.DATA.get('code', None)
            if not code:
                return Response(\
                    {'message': 'code is a required parameter'},
                    status=status.HTTP_400_BAD_REQUEST)
            try:
                code = int(code.strip())
            except ValueError:
                return Response(\
                    {'message': 'Incorrect type for code'},
                    status=status.HTTP_400_BAD_REQUEST)                
            user = self.get_object()
            if code == user.phone_number_verification_code:
                user.phone_number_verified = True
                user.save()
                return Response(\
                    {'message': 'OK'},
                    status=status.HTTP_200_OK)
            else:
                return Response(\
                    {'message': 'Incorrect code'},
                    status=status.HTTP_400_BAD_REQUEST)


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
        qs = SocialCrimeReport.objects.select_related('reporter').all()
        latitude = self.request.QUERY_PARAMS.get('latitude', None)
        longitude = self.request.QUERY_PARAMS.get('longitude', None)
        distance_within =\
            self.request.QUERY_PARAMS.get('distance_within', None)
        if (latitude and longitude) and distance_within:
            point = Point(float(longitude), float(latitude))
            dwithin = float(distance_within)
            qs = SocialCrimeReport.objects\
                .select_related('reporter')\
                .filter(report_point__dwithin=(point, D(mi=dwithin)))\
                .distance(point).order_by('distance')
        elif latitude or longitude or distance_within:
            # We got one or more values but not all we need, so return none
            qs = SocialCrimeReport.objects.none()
        return qs


class AgencyViewSet(viewsets.ModelViewSet):
    model = Agency
    serializer_class = AgencySerializer
    filter_backends = (SearchFilter,)
    search_fields = ('domain',)

    def get_queryset(self):
        qs = Agency.objects.select_related('agency_point_of_contact').all()
        latitude = self.request.QUERY_PARAMS.get('latitude', None)
        longitude = self.request.QUERY_PARAMS.get('longitude', None)
        distance_within =\
            self.request.QUERY_PARAMS.get('distance_within', None)
        if (latitude and longitude) and distance_within:
            point = Point(float(longitude), float(latitude))
            dwithin = float(distance_within)
            qs = Agency.geo.select_related('agency_point_of_contact')\
                .filter(agency_center_point__dwithin=(point,
                                                      D(mi=dwithin)))\
                .distance(point).order_by('distance')
        elif latitude or longitude or distance_within:
            # We got one or more values but not all we need, so return none
            qs = Agency.objects.none()
        return qs

    @action()
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
    queryset =\
        Alert.objects.select_related('agency', 'agency_user',
                                     'agency_dispatcher')\
        .prefetch_related('locations').all()
    serializer_class = AlertSerializer
    filter_fields = ('agency', 'agency_user', 'agency_dispatcher',
                     'status', 'initiated_by',)
    filter_class = AlertsModifiedSinceFilterBackend

    @action()
    def disarm(self, request, pk=None):
        """
        Set a disarmed time on the alert. This indicates that the user wishes
        to cancel the alert.
        """
        alert = self.get_object()
        alert.disarm()
        serialized = AlertSerializer(alert)
        return Response(serialized.data)
        

    @action()
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
            dynamo_db.save_item_to_table(\
                settings.DYNAMO_DB_CHAT_MESSAGES_TABLE,
                {'alert_id': int(pk), 'sender_id': request.user.id,
                 'message': message, 'timestamp': time.time(),
                 'message_id': message_id})
            alert = self.get_object()
            if not request.user.id == alert.agency_user.id:
                user = alert.agency_user
                notify_new_chat_message_available.delay(\
                    message, message_id,
                    user.device_type,
                    user.device_endpoint_arn)
            return Response({'message': 'Chat received'})
        else:
            return Response(\
                {'message': "message and sender are required parameters"},
                status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'])
    def messages(self, request, pk=None):
        """
        Get all messages for the given alert.
        """
        dynamo_db = DynamoDBManager()
        messages = dynamo_db.get_messages_for_alert(pk)
        return Response(messages)

    @action(methods=['get'])
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
            return Response(\
                {'message': "timestamp must be an Unix timestamp"},
                status=status.HTTP_400_BAD_REQUEST)


class AlertLocationViewSet(viewsets.ModelViewSet):
    queryset = AlertLocation.objects.select_related('alert').all()
    serializer_class = AlertLocationSerializer
    filter_fields = ('alert',)


class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.select_related().all()
    serializer_class = ChatMessageSerializer
    filter_fields = ('alert', 'sender', 'creation_date', 'last_modified',
                     'sender__agency',)


class MassAlertViewSet(viewsets.ModelViewSet):
    queryset = MassAlert.objects.select_related().all()
    serializer_class = MassAlertSerializer
    filter_fields = ('agency', 'agency_dispatcher',)


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