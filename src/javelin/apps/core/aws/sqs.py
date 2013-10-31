from django.conf import settings

import boto.sqs
from boto.sqs.connection import SQSConnection
from boto.sqs.message import RawMessage


def get_sqs_connection():
    return SQSConnection(aws_access_key_id=settings.SQS_ACCESS_KEY_ID,
                         aws_secret_access_key=settings.SQS_SECRET_ACCESS_KEY)


def get_queue(queue_name):
    connection = get_sqs_connection()
    return connection.create_queue(queue_name)


def get_alert_queue():
    return get_queue(settings.SQS_ALERT_QUEUE)


def check_alert_queue():
    queue = get_alert_queue()
    queue.set_message_class(RawMessage)
    result = queue.get_messages()
    if result:
        message = result[0]
        return message


def test_alert():
    queue = get_alert_queue()
    m = RawMessage()
    m.set_body("""{"blah": "booo", "derp": 3"}""")
    status = queue.write(m)
    print status
