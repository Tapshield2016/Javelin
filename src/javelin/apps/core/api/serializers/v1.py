from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from rest_framework import serializers

from core.models import (Agency, Alert, AlertLocation, Theme,
                         ChatMessage, MassAlert, UserProfile,
                         EntourageMember, SocialCrimeReport, Region,
                         DispatchCenter, Period, ClosedDate, StaticDevice)

from emailmgr.models import EmailAddress
from emailmgr.serializers import EmailAddressGETSerializer

User = get_user_model()


class EntourageMemberGETSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = EntourageMember
        fields = ('url', 'user', 'name')


class EntourageMemberUpdateSerializer(serializers.HyperlinkedModelSerializer):

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

    closed_date = ClosedDateSerializer(required=False, many=True)
    opening_hours = PeriodSerializer(required=False, many=True)

    class Meta:
        model = DispatchCenter

class AgencySerializer(serializers.HyperlinkedModelSerializer):
    distance = serializers.SerializerMethodField('distance_if_exists')
    dispatch_center = DispatchCenterSerializer(required=False, many=True)
    region = RegionSerializer(required=False, many=True)

    class Meta:
        model = Agency

    def distance_if_exists(self, obj):
        if getattr(obj, 'distance', None):
            return obj.distance.mi

    def to_native(self, obj):
        ret = super(AgencySerializer, self).to_native(obj)
        if obj:
            if obj.theme:
                agency_theme = ThemeSerializer(instance=obj.theme)
                ret['theme'] = agency_theme.data
            if obj.branding:
                branding_theme = ThemeSerializer(instance=obj.branding)
                ret['branding'] = branding_theme.data
        return ret


class UserSerializer(serializers.HyperlinkedModelSerializer):
    agency = serializers.HyperlinkedRelatedField(required=False,
                                                 view_name='agency-detail')
    entourage_members = EntourageMemberGETSerializer(required=False, many=True)
    distance = serializers.SerializerMethodField('distance_if_exists')

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups', 'agency', 'is_active',
                  'phone_number', 'disarm_code', 'first_name', 'last_name',
                  'phone_number_verified', 'user_declined_push_notifications',
                  'user_logged_in_via_social', 'entourage_members',
                  'last_reported_time', 'distance',)

    def to_native(self, obj):
        ret = super(UserSerializer, self).to_native(obj)
        if obj:
            email_address = EmailAddress.objects.filter(user=obj)
            address = []
            for email in email_address:
                address.append(EmailAddressGETSerializer(instance=email).data)
            ret['secondary_emails'] = address
        return ret

    def distance_if_exists(self, obj):
        if getattr(obj, 'distance', None):
            return obj.distance.mi



class UserUpdateSerializer(serializers.HyperlinkedModelSerializer):
    agency = serializers.HyperlinkedRelatedField(required=False,
                                                 view_name='agency-detail')

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups', 'agency', 'is_active',
                  'phone_number', 'disarm_code', 'first_name', 'last_name',
                  'phone_number_verified', 'user_declined_push_notifications',
                  'user_logged_in_via_social',
                  'last_reported_time', 'last_reported_latitude',
                  'last_reported_longitude')


class UnauthorizedUserSerializer(serializers.HyperlinkedModelSerializer):
    agency = serializers.HyperlinkedRelatedField(required=False,
                                                 view_name='agency-detail')

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups', 'agency', 'is_active',
                  'phone_number', 'disarm_code', 'first_name', 'last_name',
                  'phone_number_verified', 'user_declined_push_notifications',
                  'user_logged_in_via_social',
                  'last_reported_time', 'last_reported_latitude',
                  'last_reported_longitude')


class ReporterSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'phone_number', 'first_name', 'last_name',)


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

    def to_native(self, obj):
        ret = super(AlertSerializer, self).to_native(obj)
        if obj:
            if obj.agency_user:
                agency_user_meta = UserSerializer(instance=obj.agency_user)
                ret['agency_user_meta'] = agency_user_meta.data
            if obj.static_device:
                static_device_meta = StaticDeviceSerializer(instance=obj.static_device)
                ret['static_device_meta'] = static_device_meta.data
            ret['agency_dispatcher_name'] = None
            if obj.agency_dispatcher:
                ret['agency_dispatcher_name'] =\
                    obj.agency_dispatcher.get_full_name()
            ret['latest_location'] = {}
            latest_location = obj.locations.first()
            if latest_location:
                ret['latest_location'] =\
                    AlertLocationSerializer(instance=latest_location).data 
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

    def to_native(self, obj):
        ret = super(SocialCrimeReportSerializer, self).to_native(obj)
        if obj:

            if obj.viewed_by:
                ret['dispatcher_name'] =\
                    obj.viewed_by.get_full_name()
            elif obj.flagged_by_dispatcher:
                ret['dispatcher_name'] =\
                    obj.flagged_by_dispatcher.get_full_name()

        return ret

    def distance_if_exists(self, obj):
        if getattr(obj, 'distance', None):
            return obj.distance.mi


class StaticDeviceSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = StaticDevice


class ThemeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Theme