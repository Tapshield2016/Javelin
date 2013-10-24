from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from rest_framework.filters import DjangoFilterBackend, OrderingFilter
from rest_framework import viewsets

from core.serializers.v1 import (UserSerializer, GroupSerializer,
                                 AgencySerializer, AlertSerializer,
                                 ChatMessageSerializer, MassAlertSerializer,
                                 UserProfileSerializer)

from core.models import Agency, Alert, ChatMessage, MassAlert, UserProfile

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.prefetch_related('groups').all()
    serializer_class = UserSerializer
    filter_fields = ('agency',)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class AgencyViewSet(viewsets.ModelViewSet):
    queryset = Agency.objects.all()
    serializer_class = AgencySerializer


class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    filter_fields = ('agency', 'agency_user', 'agency_dispatcher',
                     'status', 'initiated_by',)


class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    filter_fields = ('alert', 'sender', 'creation_date', 'last_modified',
                     'sender__agency',)


class MassAlertViewSet(viewsets.ModelViewSet):
    queryset = MassAlert.objects.all()
    serializer_class = MassAlertSerializer
    filter_fields = ('agency', 'agency_dispatcher',)


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
