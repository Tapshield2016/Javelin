from core.models import (
    Alert,
    AlertLocation,
    ChatMessage,
    MassAlert,
    UserProfile,
    EntourageMember,
    SocialCrimeReport,
    EntourageSession,
    TrackingLocation,
    NamedLocation,
    UserNotification
)
from agency.models import Agency, Region, DispatchCenter, Period, ClosedDate, Theme, ClosedDate
from staticdevice.models import StaticDevice

from emailmgr.models import EmailAddress
from emailmgr.serializers import EmailAddressGETSerializer

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers
from rest_framework.authtoken.models import Token

User = get_user_model()


class UserNotificationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserNotification
        fields = ('url', 'user', 'title', 'message', 'type', 'read', 'creation_date',)

    def to_representation(self, obj):
        ret = super(UserNotificationSerializer, self).to_representation(obj)

        if obj:
            if obj.content_type:
                try:
                    action_obj = obj.content_type.get_object_for_this_type(pk=obj.object_id)
                    if action_obj:
                        ret['content_type'] = obj.content_type.name
                        serialized = serializer_for_unknown(action_obj, self.context.get('request', None))
                        if serialized:
                            ret['action_object'] = serialized.data
                except ObjectDoesNotExist:
                    pass
        return ret


class UnauthorizedEntourageMemberSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EntourageMember
        fields = ('url', 'user', 'name', 'matched_user')


class NamedLocationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = NamedLocation


class TrackingLocationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TrackingLocation
        fields = ('latitude', 'longitude',)


class TrackingLocationFullSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TrackingLocation


class EntourageSessionSerializer(serializers.HyperlinkedModelSerializer):
    locations = TrackingLocationSerializer(required=False, many=True, read_only=True)

    class Meta:
        model = EntourageSession
        fields = ('url', 'status', 'travel_mode', 'start_location', 'end_location', 'eta',
                  'start_time', 'arrival_time', 'entourage_notified', 'locations',)
        depth = 2


class EntourageSessionPostSerializer(serializers.HyperlinkedModelSerializer):
    locations = TrackingLocationSerializer(required=False, many=True, read_only=True)

    class Meta:
        model = EntourageSession


class EntourageMemberSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EntourageMember


class RegionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Region


class ClosedDateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ClosedDate


class PeriodSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Period


class DispatchCenterSerializer(serializers.HyperlinkedModelSerializer):
    closed_date = ClosedDateSerializer(required=False, many=True, read_only=True)
    opening_hours = PeriodSerializer(required=False, many=True, read_only=True)

    class Meta:
        model = DispatchCenter


class AgencyListSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Agency
        fields = ("url", "id", "name")



class AgencySerializer(serializers.HyperlinkedModelSerializer):
    distance = serializers.SerializerMethodField('distance_if_exists', read_only=True)
    dispatch_center = DispatchCenterSerializer(required=False, many=True, read_only=True)
    region = RegionSerializer(required=False, many=True, read_only=True)

    class Meta:
        model = Agency

    def distance_if_exists(self, obj):
        if getattr(obj, 'distance', None):
            return obj.distance.mi

    def to_representation(self, obj):
        ret = super(AgencySerializer, self).to_representation(obj)
        if obj:
            if obj.theme:
                agency_theme = ThemeSerializer(instance=obj.theme,
                                               context={'request': self.context.get('request', None)})
                ret['theme'] = agency_theme.data
            if obj.branding:
                branding_theme = ThemeSerializer(instance=obj.branding,
                                                 context={'request': self.context.get('request', None)})
                ret['branding'] = branding_theme.data
        return ret


class UserSerializer(serializers.HyperlinkedModelSerializer):
    agency = serializers.HyperlinkedRelatedField(required=False,
                                                 read_only=True,
                                                 view_name='agency-detail')
    entourage_members = EntourageMemberSerializer(required=False, many=True, read_only=True)
    distance = serializers.SerializerMethodField('distance_if_exists', read_only=True)

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups', 'agency', 'is_active',
                  'phone_number', 'disarm_code', 'first_name', 'last_name',
                  'phone_number_verified', 'user_declined_push_notifications',
                  'user_logged_in_via_social', 'entourage_members', 'distance')

    def to_representation(self, user):
        ret = super(UserSerializer, self).to_representation(user)
        if user:
            email_address = EmailAddress.objects.filter(user=user)
            address = []
            for email in email_address:
                address.append(EmailAddressGETSerializer(instance=email,
                                                         context={'request': self.context.get('request', None)}).data)
            ret['secondary_emails'] = address

            active_session = EntourageSession.tracking.filter(user=user)
            if active_session:
                ret['entourage_session'] = EntourageSessionSerializer(instance=active_session[0],
                                                                      context={'request': self.context.get('request',
                                                                                                           None)}).data

        return ret

    def distance_if_exists(self, obj):
        if getattr(obj, 'distance', None):
            return obj.distance.mi


class UserLoginSerializer(UserSerializer):
    def to_representation(self, user):
        ret = super(UserLoginSerializer, self).to_representation(user)
        if user:
            if user.agency:
                ret['agency'] = AgencySerializer(user.agency,
                                                 context={'request': self.context.get('request', None)}).data
            token, created = Token.objects.get_or_create(user=user)
            ret['token'] = token.key

        return ret


class PostUserSerializer(serializers.HyperlinkedModelSerializer):
    agency = serializers.HyperlinkedRelatedField(required=False,
                                                 read_only=True,
                                                 view_name='agency-detail')
    entourage_members = EntourageMemberSerializer(required=False,
                                                  read_only=True,
                                                  many=True)

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups', 'agency', 'is_active',
                  'phone_number', 'disarm_code', 'first_name', 'last_name',
                  'phone_number_verified', 'user_declined_push_notifications',
                  'user_logged_in_via_social', 'entourage_members', 'location_timestamp',
                  'latitude', 'longitude', 'accuracy', 'altitude', 'floor_level',)

    def to_representation(self, user):
        ret = super(PostUserSerializer, self).to_representation(user)
        if user:
            email_address = EmailAddress.objects.filter(user=user)
            address = []
            for email in email_address:
                address.append(EmailAddressGETSerializer(instance=email,
                                                         context={'request': self.context.get('request', None)}).data)
            ret['secondary_emails'] = address

            active_session = EntourageSession.tracking.filter(user=user)
            if active_session:
                ret['entourage_session'] = EntourageSessionSerializer(instance=active_session[0],
                                                                      context={'request': self.context.get('request',
                                                                                                           None)}).data

        return ret

    # def update(self, instance, validated_data):
    #     # agency_data = validated_data.pop('agency')
    #     # Unless the application properly enforces that this field is
    #     # always set, the follow could raise a `DoesNotExist`, which
    #     # would need to be handled.
    #     instance.save()
    #
    #     return instance


class UserAlwaysVisibleEntourageMemberSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'agency',
                  'phone_number', 'first_name', 'last_name',
                  'location_timestamp', 'latitude', 'longitude',
                  'accuracy', 'altitude', 'floor_level',)

    def to_representation(self, user):
        ret = super(UserAlwaysVisibleEntourageMemberSerializer, self).to_representation(user)
        if user:
            active_session = EntourageSession.tracking.filter(user=user)
            if active_session:
                ret['entourage_session'] = EntourageSessionSerializer(instance=active_session[0],
                                                                      context={'request': self.context.get('request',
                                                                                                           None)}).data
        return ret


class UserTrackingEntourageMemberSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'agency',
                  'phone_number', 'first_name', 'last_name')

    def to_representation(self, user):
        ret = super(UserTrackingEntourageMemberSerializer, self).to_representation(user)
        if user:
            active_session = EntourageSession.tracking.filter(user=user)
            if active_session:
                ret = UserAlwaysVisibleEntourageMemberSerializer(instance=user,
                                                                 context={
                                                                     'request': self.context.get('request', None)}).data
        return ret


class UserNoLocationEntourageMemberSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'agency',
                  'phone_number', 'first_name', 'last_name')


class UnauthorizedUserSerializer(serializers.HyperlinkedModelSerializer):
    agency = serializers.HyperlinkedRelatedField(required=False,
                                                 read_only=True,
                                                 view_name='agency-detail')

    class Meta:
        model = User
        fields = ('url', 'agency', 'first_name', 'last_name', 'username', 'email')


class DispatcherUserSerializer(serializers.HyperlinkedModelSerializer):
    agency = serializers.HyperlinkedRelatedField(required=False,
                                                 read_only=True,
                                                 view_name='agency-detail')

    class Meta:
        model = User
        fields = ('url', 'agency', 'first_name', 'last_name', 'username', 'email', 'phone_number' 'disarm_code',
                  'location_timestamp', 'latitude', 'longitude', 'accuracy', 'altitude', 'floor_level',)


class ReporterSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'email', 'phone_number', 'first_name', 'last_name',)


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class AlertLocationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AlertLocation


class AlertSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Alert

    def to_representation(self, obj):
        ret = super(AlertSerializer, self).to_representation(obj)
        if obj:
            if obj.agency_user:
                agency_user_meta = UserSerializer(instance=obj.agency_user,
                                                  context={'request': self.context.get('request', None)})
                ret['agency_user_meta'] = agency_user_meta.data
            if obj.static_device:
                static_device_meta = StaticDeviceSerializer(instance=obj.static_device,
                                                            context={'request': self.context.get('request', None)})
                ret['static_device_meta'] = static_device_meta.data
            ret['agency_dispatcher_name'] = None
            if obj.agency_dispatcher:
                ret['agency_dispatcher_name'] = \
                    obj.agency_dispatcher.get_full_name()
            ret['latest_location'] = {}
            if obj.locations:
                latest_location = obj.locations.first()
                if latest_location:
                    ret['latest_location'] = \
                        AlertLocationSerializer(instance=latest_location,
                                                context={'request': self.context.get('request', None)}).data
        return ret


class AlertLimitedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Alert

    def to_representation(self, obj):
        ret = super(AlertLimitedSerializer, self).to_representation(obj)
        if obj:
            if obj.agency_user:
                agency_user_meta = UnauthorizedUserSerializer(instance=obj.agency_user,
                                                              context={'request': self.context.get('request', None)})
                ret['agency_user'] = agency_user_meta.data

            ret['latest_location'] = {}
            latest_location = obj.locations.first()
            if latest_location:
                ret['latest_location'] = \
                    AlertLocationSerializer(instance=latest_location,
                                            context={'request': self.context.get('request', None)}).data
        return ret


class ChatMessageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ChatMessage


class MassAlertSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MassAlert


class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserProfile


class SocialCrimeReportSerializer(serializers.HyperlinkedModelSerializer):
    distance = serializers.SerializerMethodField('distance_if_exists')

    class Meta:
        model = SocialCrimeReport

    def to_representation(self, obj):
        ret = super(SocialCrimeReportSerializer, self).to_representation(obj)
        if obj:

            if obj.viewed_by:
                ret['dispatcher_name'] = \
                    obj.viewed_by.get_full_name()
            elif obj.flagged_by_dispatcher:
                ret['dispatcher_name'] = \
                    obj.flagged_by_dispatcher.get_full_name()

        return ret

    def distance_if_exists(self, obj):
        if getattr(obj, 'distance', None):
            return obj.distance.mi


class StaticDeviceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = StaticDevice


class ThemeSerializer(serializers.HyperlinkedModelSerializer):
    small_logo = serializers.CharField(source='small_logo_s3_url', read_only=True)
    navbar_logo = serializers.CharField(source='navbar_logo_s3_url', read_only=True)
    navbar_logo_alternate = serializers.CharField(source='navbar_logo_alternate_s3_url', read_only=True)
    map_overlay_logo = serializers.CharField(source='map_overlay_logo_s3_url', read_only=True)

    class Meta:
        model = Theme


def serializer_for_unknown(obj, request):
    if isinstance(obj, EntourageSession):
        return EntourageSessionSerializer(instance=obj, context={'request': request})

    if isinstance(obj, EntourageMember):
        return EntourageMemberSerializer(instance=obj, context={'request': request})

    if isinstance(obj, User):
        return UserAlwaysVisibleEntourageMemberSerializer(instance=obj, context={'request': request})

    if isinstance(obj, SocialCrimeReport):
        return SocialCrimeReportSerializer(instance=obj, context={'request': request})

    if isinstance(obj, NamedLocation):
        return NamedLocationSerializer(instance=obj, context={'request': request})

    if isinstance(obj, TrackingLocation):
        return TrackingLocationFullSerializer(instance=obj, context={'request': request})

    if isinstance(obj, AlertLocation):
        return AlertLocationSerializer(instance=obj, context={'request': request})

    if isinstance(obj, Alert):
        return AlertLimitedSerializer(instance=obj, context={'request': request})

    if isinstance(obj, MassAlert):
        return MassAlertSerializer(instance=obj, context={'request': request})

    return None
