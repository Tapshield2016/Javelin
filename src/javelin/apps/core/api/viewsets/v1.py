import time
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import DjangoFilterBackend, OrderingFilter
from rest_framework.response import Response

from core.api.serializers.v1 import (UserSerializer, GroupSerializer,
                                     AgencySerializer, AlertSerializer,
                                     ChatMessageSerializer,
                                     MassAlertSerializer,
                                     UserProfileSerializer)

from core.aws.dynamodb import DynamoDBManager
from core.aws.sns import SNSManager
from core.models import Agency, Alert, ChatMessage, MassAlert, UserProfile
from core.tasks import (create_user_device_endpoint, publish_to_agency_topic,
                        publish_to_device, notify_new_chat_message_available)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related('agency')\
        .prefetch_related('groups').all()
    serializer_class = UserSerializer
    filter_fields = ('agency',)

    @action()
    def update_device_token(self, request, pk=None):
        if request.user.is_superuser or request.user.pk == int(pk):
            token = request.DATA.get('deviceToken', None)
            if not token:
                return Response(\
                    {'message': 'deviceToken is a required parameter'},
                    status=status.HTTP_400_BAD_REQUEST)
            else:
                try:
                    user = self.get_object()
                    user.device_token = token
                    user.save()
                    create_user_device_endpoint.delay(user.pk,
                                                      user.device_token)
                    return Response({'message': 'Success'})
                except User.DoesNotExit:
                    return Response({'message': 'user not found'},
                                    status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Not found.'},
                         status=status.HTTP_404_NOT_FOUND)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class AgencyViewSet(viewsets.ModelViewSet):
    queryset = Agency.objects.select_related('agency_point_of_contact').all()
    serializer_class = AgencySerializer

    @action()
    def send_mass_alert(self, request, pk=None):
        message = request.DATA.get('message', None)
        if not message:
            return Response({'message': 'message is a required parameter'},
                            status=status.HTTP_400_BAD_REQUEST)

        sns = SNSManager()
        agency = self.get_object()
        publish_to_agency_topic.delay(agency.sns_primary_topic_arn, message)
        return Response({'message': 'Ok'},
                        status=status.HTTP_200_OK)


class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.select_related().all()
    serializer_class = AlertSerializer
    filter_fields = ('agency', 'agency_user', 'agency_dispatcher',
                     'status', 'initiated_by',)

    @action()
    def send_message(self, request, pk=None):
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
                    user.device_endpoint_arn)
            return Response({'message': 'Chat received'})
        else:
            return Response(\
                {'message': "message and sender are required parameters"},
                status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'])
    def messages(self, request, pk=None):
        dynamo_db = DynamoDBManager()
        table = dynamo_db.get_table(settings.DYNAMO_DB_CHAT_MESSAGES_TABLE)
        results = table.query(alert_id__eq=int(pk))
        messages = []
        for res in results:
            messages.append(dict([(key, val) for key, val in res.items()]))
        return Response(messages)

    @action(methods=['get'])
    def messages_since(self, request, pk=None):
        timestamp = request.GET.get('timestamp', None)
        if not timestamp:
            return Response({'message': 'timestamp is a required parameter'},
                             status=status.HTTP_400_BAD_REQUEST)
        try:
            timestamp = float(timestamp)
            dynamo_db = DynamoDBManager()
            table = dynamo_db.get_table(settings.DYNAMO_DB_CHAT_MESSAGES_TABLE)
            results = table.query(alert_id__eq=int(pk),
                                  timestamp__gte=timestamp,
                                  index='MessageTimeIndex')
            messages = []
            for res in results:
                messages.append(dict([(key, val) for key, val in res.items()]))
            return Response(messages)
        except ValueError:
            return Response(\
                {'message': "timestamp must be an Unix timestamp"},
                status=status.HTTP_400_BAD_REQUEST)


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
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    filter_fields = ('user',)
