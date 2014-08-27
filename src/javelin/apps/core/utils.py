import time
import uuid
import ast
import re

from django.conf import settings

from core.aws.dynamodb import DynamoDBManager
from core.models import Agency, AgencyUser
from core.tasks import notify_new_chat_message_available
from django.contrib.auth.decorators import user_passes_test


def send_message_to_user_for_alert(alert, message):
    message_id = str(uuid.uuid1())
    if not alert.agency_dispatcher:
        # If no dispatcher assigned to alert, get last logged in dispatcher
        # from agency and use as sender.
        last_logged_in =\
            AgencyUser.objects.filter(agency=alert.agency,
                                      groups__name='Dispatchers')\
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
    if len(message) > 112:
        # truncate to prevent issue with push notification send
        message = "%s..." % message[:109]
    notify_new_chat_message_available.delay(\
        message, message_id,
        alert.agency_user.device_type,
        alert.agency_user.device_endpoint_arn)


def get_agency_from_unknown(unknown_object):

    agency = None

    try:
        agency = Agency.objects.get(name__iexact=unknown_object)
    except Agency.DoesNotExist:
        agency_id = ''.join(x for x in unknown_object if x.isdigit())
        if type(ast.literal_eval(agency_id)) is int:
            try:
                agency = Agency.objects.get(pk=agency_id)
            except Agency.DoesNotExist:
                return None

    return agency


def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""
    def in_groups(u):
        if u.is_authenticated():
            if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
                return True
        return False
    return user_passes_test(in_groups)