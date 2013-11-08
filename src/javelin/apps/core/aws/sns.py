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
        return self.connection.create_platform_endpoint(settings.SNS_IOS_ARN,
                                                        token=device_token)

    def create_ios_endpoint(self, device_token):
        return self.create_endpoint(settings.SNS_IOS_ARN, device_token)

    def create_topic(self, topic_name):
        topic_name = slugify(topic_name)
        return self.connection.create_topic(topic_name)

    def subscribe(self, agency_topic_arn, protocol, user_device_endpoint):
        return self.connection.subscribe(agency_topic_arn, protocol,
                                         user_device_endpoint)
