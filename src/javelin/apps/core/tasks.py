from celery import task

from django.conf import settings
from django.contrib.auth import get_user_model

from core.aws.sns import SNSManager
from core.aws.sqs import SQSManager
from core.models import Alert, Agency, AgencyUser

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
        notify_alert_received.delay(incoming_alert.id,
                                    message['agency_user'].device_endpoint_arn)
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
                user = User.objects.select_related('agency').get(pk=user_id)
                user.device_endpoint_arn = endpoint_arn
                user.save()
                if user.agency.sns_primary_topic_arn:
                    sns.subscribe(user.agency.sns_primary_topic_arn,
                                  'Application', user.device_endpoint_arn)


@task
def create_agency_topic(agency_id, topic_name=None):
    """
    We expect to see a response that is something like this:
    {u'CreateTopicResponse':
        {u'ResponseMetadata':
            {u'RequestId': u'020a88af-aec2-5532-9f34-c258a2739126'},
             u'CreateTopicResult': {u'TopicArn': u'arn:aws:sns:us-east-1:175861827001:Test_Agency'}}}
    """
    agency = Agency.objects.get(pk=agency_id)
    if not topic_name:
        topic_name = agency.name
    sns = SNSManager()
    response = sns.create_topic(topic_name)
    if 'CreateTopicResponse' in response:
        response = response['CreateTopicResponse']
        if 'CreateTopicResult' in response:
            result = response['CreateTopicResult']
            if 'TopicArn' in result:
                agency_topic_arn = result['TopicArn']
                agency.sns_primary_topic_arn = agency_topic_arn
                agency.save()


@task
def publish_to_agency_topic(agency_topic_arn, message):
    sns = SNSManager()
    return sns.publish_to_topic(message, agency_topic_arn)


@task
def publish_to_device(device_endpoint_arn, message):
    sns = SNSManager()
    return sns.publish_to_device(message, device_endpoint_arn)


@task
def notify_alert_received(alert_id, device_endpoint_arn):
    sns = SNSManager()
    msg = sns.get_message_json("The authorities have been notified of your emergency, and help is on the way!", "alert-received", alert_id)
    sns.publish_to_device(msg, device_endpoint_arn)


@task
def notify_new_chat_message_available(chat_message, chat_message_id,
                                      device_endpoint_arn):
    sns = SNSManager()
    msg = sns.get_message_json("APNS_SANDBOX", chat_message,
                               "chat-message-available", chat_message_id)
    sns.publish_to_device(msg, device_endpoint_arn)
