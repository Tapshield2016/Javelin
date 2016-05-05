from django.conf import settings
from django.template.defaultfilters import slugify

from boto.sns import SNSConnection


def ios_message_json(message_body, alert_type, alert_id):
    prefix = """"{\\"aps\\": {\\"alert\\": """
    middle = """{\\"body\\":\\"%s\\", \\"alert_type\\": \\"%s\\", \\"alert_id\\": \\"%s\\"}""" % (
        message_body,
        alert_type,
        alert_id
    )
    post = """, \\"badge\\": 1, \\"sound\\": \\"default\\"}}", """
    return prefix + middle + post

def android_message_json(message_body, alert_type, alert_id):
    msg_android = """ "{ \\"data\\": { \\"message\\": \\"%s\\", \\"alert_type\\": \\"%s\\", \\"alert_id\\": \\"%s\\"}}" """
    return msg_android % (
        message_body,
        alert_type,
        alert_id
    )

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

    @staticmethod
    def get_topic_message_json(message_body, alert_type, alert_id):
        msg_json = """{"default": \"%s\", "%s": "{\\"aps\\": {\\"alert\\": {\\"body\\":\\"%s\\", \\"alert_type\\": \\"%s\\", \\"alert_id\\": \\"%s\\"}, \\"badge\\": 1, \\"sound\\": \\"default\\"}}", "%s": "{ \\"data\\": { \\"message\\": \\"%s\\", \\"alert_type\\": \\"%s\\", \\"alert_id\\": \\"%s\\"}}"}""" % (
            message_body,
            settings.SNS_IOS_PLATFORM,
            message_body, alert_type,
            alert_id, settings.SNS_ANDROID_PLATFORM,
            message_body,
            alert_type,
            alert_id
        )
        return msg_json

    @staticmethod
    def get_message_json(endpoint, message_body, alert_type, alert_id, title):
        if endpoint == settings.SNS_APP_ENDPOINTS["I"]:
            msg_json = """{"%s": "{\\"aps\\": {\\"alert\\": {\\"body\\":\\"%s\\", \\"alert_type\\": \\"%s\\", \\"alert_id\\": \\"%s\\"}, \\"badge\\": 1, \\"sound\\": \\"default\\", \\"content-available\\": 1}}"}""" % (
                endpoint,
                message_body,
                alert_type,
                alert_id
            )
        elif endpoint == settings.SNS_APP_ENDPOINTS["A"]:
            msg_json = """{"%s": "{ \\"data\\": { \\"message\\": \\"%s\\", \\"alert_type\\": \\"%s\\", \\"alert_id\\": \\"%s\\", \\"title\\": \\"%s\\"}}"}""" % (
                endpoint,
                message_body,
                alert_type,
                alert_id,
                title
            )
        else:
            msg_json = """{"default": "%s"}""" % message_body
        return msg_json
