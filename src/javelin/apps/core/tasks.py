from celery import task
from django.conf import settings
from core.aws.sqs import SQSManager


@task
def get_new_alerts(message):
    print message
