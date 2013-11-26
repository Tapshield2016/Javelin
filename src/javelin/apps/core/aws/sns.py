from django.conf import settings
from django.template.defaultfilters import slugify

import boto.sns
from boto.sns import SNSConnection


class SNSManager(object):

    def __init__(self):
        self.connection = self.get_sqs_connection()

    def get_sqs_connection(self):
        return SNSConnection(\
            aws_access_key_id=settings.SNS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.SNS_SECRET_ACCESS_KEY)

    def create_endpoint(self, arn, device_token):
        return self.connection.create_platform_endpoint(arn,
                                                        token=device_token)

    def create_android_endpoint(self, device_token):
        return self.create_endpoint(settings.SNS_ANDROID_ARN, device_token)

    def create_ios_endpoint(self, device_token):
        return self.create_endpoint(settings.SNS_IOS_ARN, device_token)

    def create_topic(self, topic_name):
        topic_name = slugify(topic_name)
        return self.connection.create_topic(topic_name)

    def subscribe(self, agency_topic_arn, protocol, device_endpoint_arn):
        return self.connection.subscribe(agency_topic_arn, protocol,
                                         device_endpoint_arn)

    def publish_to_device(self, message_json, device_endpoint_arn):
        return self.connection.publish(message=message_json,
                                       message_structure='json',
                                       target_arn=device_endpoint_arn)

    def publish_to_topic(self, message, agency_topic_arn):
        return self.connection.publish(message=message,
                                       message_structure='json',
                                       topic=agency_topic_arn)

    def get_topic_message_json(self, message_body, alert_type, alert_id):
        msg_json ="""{"default": \"%s\", "%s": "{\\"aps\\": {\\"alert\\": {\\"body\\":\\"%s\\", \\"alert_type\\": \\"%s\\", \\"alert_id\\": \\"%s\\"}, \\"badge\\": 1}}", 
    "%s": "{ \\"data\\": { \\"message\\": \\"%s\\" }, \\"alert_type\\": \\"%s\\", \\"alert_id\\": \\"%s\\" }"}""" % (message_body, settings.SNS_IOS_PLATFORM, message_body, alert_type, alert_id, settings.SNS_ANDROID_PLATFORM, message_body, alert_type, alert_id)
        return msg_json
    

    def get_message_json(self, endpoint, message_body, alert_type, alert_id):
        msg_json = """{"%s": "{\\"aps\\": {\\"alert\\": {\\"body\\":\\"%s\\", \\"alert_type\\": \\"%s\\", \\"alert_id\\": \\"%s\\"}, \\"badge\\": 1}}"}""" % (endpoint, message_body, alert_type, alert_id)
        return msg_json