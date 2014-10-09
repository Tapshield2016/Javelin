import re
from datetime import datetime, timedelta
from django.utils.timezone import utc

from celery import task

from django_twilio.client import twilio_client

from django.conf import settings
from django.contrib.auth import get_user_model

from core.aws.s3 import S3Manager
from core.aws.sns import SNSManager
from core.aws.sqs import SQSManager
from core.models import Agency, AgencyUser, Alert, AlertLocation, StaticDevice
from core.api.serializers.v1 import AlertSerializer

User = get_user_model()


@task
def new_alert(message):
    """
    We expect to see a message that's something like this:

      {u'location_latitude': 37.33233141,
       u'location_altitude': 0,
       u'location_longitude': -122.0312186,
       u'location_accuracy': 5,
       u'user': u'ben@benboyd.us'
       u'agency': 1}
    """
    message_valid = False
    if 'user' in message:
        user = AgencyUser.objects.get(username=message['user'])
        location_latitude = message['location_latitude']
        location_longitude = message['location_longitude']
        location_altitude = message['location_altitude']
        location_accuracy = message['location_accuracy']
        alert_initiated_by = message['alert_type']

        agency = user.agency

        if 'agency' in message:
            agency = Agency.objects.get(pk=message['agency'])

        active_alerts = Alert.active.filter(agency_user=user)

        incoming_alert = None

        if active_alerts:
            past_alert = active_alerts[0]
            #complete past alerts that are no longer relevant
            if past_alert.agency != agency:
                past_alert.status = "C"
                past_alert.save()
            elif past_alert.accepted_time:
                #Time zone aware comparison required
                if (datetime.utcnow().replace(tzinfo=utc) - past_alert.accepted_time) > timedelta(hours = 1):
                    past_alert.status = "C"
                    past_alert.save()
                else:
                    incoming_alert = past_alert
                    incoming_alert.disarmed_time = None
            else:
                incoming_alert = past_alert
                incoming_alert.disarmed_time = None

        if not incoming_alert:
            incoming_alert = Alert(agency=agency, agency_user=user,
                                   initiated_by=alert_initiated_by)


        if alert_initiated_by == "N" and not agency.emergency_call_available:
            incoming_alert.status = "U"
        elif alert_initiated_by == "E" and not agency.alert_available:
            incoming_alert.status = "U"
        elif alert_initiated_by == "T" and not agency.entourage_available:
            incoming_alert.status = "U"
        elif alert_initiated_by == "Y" and not agency.yank_available:
            incoming_alert.status = "U"
        elif alert_initiated_by == "C" and not agency.chat_available:
            incoming_alert.status = "U"
        elif alert_initiated_by == "S" and not agency.static_device_available:
            incoming_alert.status = "U"

        incoming_alert.save()

        incoming_alert_location = AlertLocation(alert=incoming_alert,
                                                altitude=location_altitude,
                                                longitude=location_longitude,
                                                latitude=location_latitude,
                                                accuracy=location_accuracy)
        incoming_alert_location.save()

        message_valid = True
        serialized = AlertSerializer(instance=incoming_alert)


        if incoming_alert.status != "U" and incoming_alert.alert_initiated_by != "C":
            notify_alert_received.delay(serialized.data['url'],
                                    user.device_type,
                                    user.device_endpoint_arn)
            incoming_alert.user_notified_of_receipt = True
        incoming_alert.save()

        if user.agency.enable_chat_autoresponder:
            notify_waiting_users_of_congestion(user.agency.id,
                                               [incoming_alert.id,])
    else:
        pass

    return message_valid


@task
def send_phone_number_verification(phone_number, verification_code):
    phone_number = re.sub("\D", "", phone_number)
    phone_number = "+1%s" % phone_number[-10:]
    resp = twilio_client.messages.create(\
        to=phone_number,
        from_=settings.TWILIO_SMS_FROM_NUMBER,
        body="Your TapShield verification code is: %s" % verification_code)


@task
def create_user_device_endpoint(user_id, device_type, device_token):
    """
    We expect to see a response that is something like this:
    {u'CreatePlatformEndpointResponse':
        {u'CreatePlatformEndpointResult':
            {u'EndpointArn': u'arn:aws:sns:us-east-1:175861827001:endpoint/APNS_SANDBOX/Javelin-iOS-Dev/b0df0f39-8171-3c4d-b510-b01db17e8c64'},
         u'ResponseMetadata':
            {u'RequestId': u'f1cf7de0-6c5b-5492-b7aa-37169d3f1cd8'}}}
    """
    sns = SNSManager()
    response = {}
    if device_type == "I":
        response = sns.create_ios_endpoint(device_token)
    elif device_type == "A":
        response = sns.create_android_endpoint(device_token)
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
    topic_suffix = ''
    if settings.DEBUG:
        topic_suffix = '-dev'
    else:
        topic_suffix = '-prod'
    response = sns.create_topic(topic_name + topic_suffix)
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
    msg = sns.get_topic_message_json(message, "mass-alert", "heyyyy")
    sns.publish_to_topic(msg, agency_topic_arn)


@task
def request_location_from_agency_topic_members(agency_topic_arn, message):
    sns = SNSManager()
    msg = get_location_report_topic_message_json()
    return sns.publish_to_topic(msg, agency_topic_arn)


@task
def request_location_from_single_agency_member(device_type,
                                               device_endpoint_arn):
    sns = SNSManager()
    app_endpoint = settings.SNS_APP_ENDPOINTS.get(device_type, None)
    msg = get_location_report_topic_message_json(app_endpoint)
    return sns.publish_to_device(msg, device_endpoint_arn)


@task
def publish_to_device(device_endpoint_arn, message):
    sns = SNSManager()
    return sns.publish_to_device(message, device_endpoint_arn)


@task
def notify_alert_completed(message, device_type, device_endpoint_arn):
    sns = SNSManager()
    app_endpoint = settings.SNS_APP_ENDPOINTS.get(device_type, None)
    msg = sns.get_message_json(app_endpoint, message, "chat-message-available",
                               "alert-completed", "Alert Completed")
    sns.publish_to_device(msg, device_endpoint_arn)


@task
def notify_alert_received(alert_id, device_type, device_endpoint_arn):
    sns = SNSManager()
    app_endpoint = settings.SNS_APP_ENDPOINTS.get(device_type, None)
    msg = sns.get_message_json(app_endpoint, "The authorities have been notified of your emergency, and help is on the way!",
                               "alert-received", alert_id, "Alert Received")
    sns.publish_to_device(msg, device_endpoint_arn)


@task
def notify_new_chat_message_available(chat_message, chat_message_id,
                                      device_type, device_endpoint_arn):
    sns = SNSManager()
    app_endpoint = settings.SNS_APP_ENDPOINTS.get(device_type, None)
    msg = sns.get_message_json(app_endpoint, chat_message,
                               "chat-message-available", chat_message_id, "New Message")
    sns.publish_to_device(msg, device_endpoint_arn)


@task
def notify_crime_report_marked_viewed(message, crime_report_id,
                                   device_type, device_endpoint_arn):
    sns = SNSManager()
    app_endpoint = settings.SNS_APP_ENDPOINTS.get(device_type, None)
    msg = sns.get_message_json(app_endpoint, message,
                               "crime-report", crime_report_id, "Crime Report Viewed")
    sns.publish_to_device(msg, device_endpoint_arn)


@task
def delete_file_from_s3(url):
    s3 = S3Manager()
    s3.delete_file(url)


@task
def notify_waiting_users_of_congestion(agency_id, alert_ids=None):
    from core.utils import send_message_to_user_for_alert
    agency = Agency.objects.get(pk=agency_id)
    waiting_alerts =\
        Alert.should_receive_autoresponse.filter(agency=agency)
    if alert_ids:
        waiting_alerts = waiting_alerts.filter(pk__in=alert_ids)
    for alert in waiting_alerts:
        send_message_to_user_for_alert(alert,
                                       agency.chat_autoresponder_message)
        alert.user_notified_of_dispatcher_congestion = True
        alert.save()


@task
def new_static_alert(device):

    """
    Starts an alert using the stationary device coordinates
    """

    location_latitude = device.latitude
    location_longitude = device.longitude
    alert_initiated_by = "S"

    active_alerts = Alert.active.filter(static_device=device)
    if active_alerts:
        incoming_alert = active_alerts[0]
        incoming_alert.disarmed_time = None
    else:
        incoming_alert = Alert(agency=device.agency, static_device=device,
                               initiated_by=alert_initiated_by)
        incoming_alert.save()

    incoming_alert_location = AlertLocation(alert=incoming_alert,
                                            # altitude=location_altitude,
                                            longitude=location_longitude,
                                            latitude=location_latitude,)
                                            # accuracy=location_accuracy)
    incoming_alert_location.save()
    incoming_alert.user_notified_of_receipt = True
    incoming_alert.save()

    return incoming_alert
