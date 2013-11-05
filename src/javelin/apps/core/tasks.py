from celery import task

from django.conf import settings

from core.aws.sqs import SQSManager
from core.models import Alert, AgencyUser


@task
def new_alert(message):
    """
    We expect to see a message that's something like this:

      {u'location_latitude': 37.33233141,
       u'location_altitude': 0,
       u'location_longitude': -122.0312186,
       u'location_accuracy': 5,
       u'user': u'ben@benboyd.us'}
    """
    message_valid = False
    if 'user' in message:
        message['agency_user'] = AgencyUser.objects.get(email=message['user'])
        del message['user']
        incoming_alert = Alert(**message)
        incoming_alert.agency = message['agency_user'].agency
        incoming_alert.save()
        message_valid = True
    else:
        pass

    return message_valid
