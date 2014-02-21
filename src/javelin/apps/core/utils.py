import time
import uuid

from django.conf import settings

from core.aws.dynamodb import DynamoDBManager
from core.models import Agency, AgencyUser
from core.tasks import notify_new_chat_message_available


def send_message_to_user_for_alert(alert, message):
    message_id = str(uuid.uuid1())
    if not alert.agency_dispatcher:
        # If no dispatcher assigned to alert, get last logged in dispatcher
        # from agency and use as sender.
        last_logged_in =\
            AgencyUser.objects.filter(agency=alert.agency)\
            .order_by('-last_login')
        if last_logged_in:
            sender_id = last_logged_in[0].id
    else:
        sender_id = alert.agency_dispatcher.id
    dynamo_db = DynamoDBManager()
    dynamo_db.save_item_to_table(\
        settings.DYNAMO_DB_CHAT_MESSAGES_TABLE,
        {'alert_id': alert.id, 'sender_id': sender_id,
         'message': message, 'timestamp': time.time(),
         'message_id': message_id})
    user = alert.agency_user
    notify_new_chat_message_available.delay(\
        message, message_id,
        alert.agency_user.device_type,
        alert.agency_user.device_endpoint_arn)
