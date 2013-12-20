from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from rest_framework import serializers

from core.models import (Agency, Alert, AlertLocation,
                         ChatMessage, MassAlert, UserProfile)

User = get_user_model()


class AgencySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Agency


class UserSerializer(serializers.HyperlinkedModelSerializer):
    agency = serializers.HyperlinkedRelatedField(required=False,
                                                 view_name='agency-detail')

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups', 'agency', 'is_active',
                  'phone_number', 'disarm_code', 'first_name', 'last_name')


class GroupSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Group
        fields = ('url', 'name')


class AlertLocationSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = AlertLocation


class LatestAlertLocationSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = AlertLocation


class AlertSerializer(serializers.HyperlinkedModelSerializer):
    locations = LatestAlertLocationSerializer(many=False, required=False)

    class Meta:
        model = Alert


class ChatMessageSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ChatMessage


class MassAlertSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = MassAlert


class UserProfileSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = UserProfile
