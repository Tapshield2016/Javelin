from celery import task

from django.conf import settings
from django.contrib.auth import get_user_model

from core.aws.sns import SNSManager
from core.aws.sqs import SQSManager
from core.models import Alert, AgencyUser

User = get_user_model()


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


@task
def create_user_device_endpoint(user_id, device_token):
    """
    We expect to see a response that is something like this:
    {u'CreatePlatformEndpointResponse':
        {u'CreatePlatformEndpointResult':
            {u'EndpointArn': u'arn:aws:sns:us-east-1:175861827001:endpoint/APNS_SANDBOX/Javelin-iOS-Dev/b0df0f39-8171-3c4d-b510-b01db17e8c64'},
         u'ResponseMetadata':
            {u'RequestId': u'f1cf7de0-6c5b-5492-b7aa-37169d3f1cd8'}}}
    """
    sns = SNSManager()
    response = sns.create_ios_endpoint(device_token)
    if 'CreatePlatformEndpointResponse' in response:
        response = response['CreatePlatformEndpointResponse']
        if 'CreatePlatformEndpointResult' in response:
            result = response['CreatePlatformEndpointResult']
            if 'EndpointArn' in result:
                endpoint_arn = result['EndpointArn']
                user = User.objects.get(pk=user_id)
                user.device_endpoint_arn = endpoint_arn
                user.save()
