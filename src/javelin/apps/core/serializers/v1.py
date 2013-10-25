from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from rest_framework import serializers

from core.models import Agency, Alert, ChatMessage, MassAlert, UserProfile

User = get_user_model()


class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups',
                  'agency', 'device_token',)


class GroupSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Group
        fields = ('url', 'name')


class AgencySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Agency


class AlertSerializer(serializers.HyperlinkedModelSerializer):

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
