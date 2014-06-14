from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from rest_framework import serializers

from core.models import (Agency, Alert, AlertLocation,
                         ChatMessage, MassAlert, UserProfile,
                         EntourageMember, SocialCrimeReport, Region,
                         DispatchCenter, DispatcherTimes, ClosedDate, Day, Schedule)

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

class DispatcherTimesSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = DispatcherTimes

class ScheduleSerializer(serializers.HyperlinkedModelSerializer):

    monday = DispatcherTimesSerializer(required=False, many=True)

    class Meta:
        model = Schedule

class DaySerializer(serializers.HyperlinkedModelSerializer):

    time = DispatcherTimesSerializer(required=False, many=True)

    class Meta:
        model = Day


class DispatchCenterSerializer(serializers.HyperlinkedModelSerializer):

    # closed_dates = ClosedDateSerializer(required=False, many=True)
    # schedule = ScheduleSerializer(required=False)

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
                  'last_reported_time', 'distance')

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
            agency_user_meta = UserSerializer(instance=obj.agency_user)
            ret['agency_user_meta'] = agency_user_meta.data
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

    def distance_if_exists(self, obj):
        if getattr(obj, 'distance', None):
            return obj.distance.mi
