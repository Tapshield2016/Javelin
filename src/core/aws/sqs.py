from django.conf import settings

from boto.sqs.connection import SQSConnection


class SQSManager(object):

    def __init__(self):
        self.connection = self.get_sqs_connection()

    def get_sqs_connection(self):
        return SQSConnection(\
            aws_access_key_id=settings.SQS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.SQS_SECRET_ACCESS_KEY)

    def get_queue(self, queue_name):
        return self.connection.create_queue(queue_name)

    def get_alert_queue(self):
        return self.get_queue(settings.SQS_ALERT_QUEUE)

    def check_alert_queue(self, num_messages=1):
        queue = self.get_alert_queue()
        #queue.set_message_class(RawMessage)
        messages = queue.get_messages(num_messages=num_messages)
        return messages
