from celery import task
from django.conf import settings
from core.aws.sqs import SQSManager


@task
def get_new_alerts():
    print "HEY!!!!!!!!\n\n\n\n\n\n\n\nHEY!!!!!!!!!!!!\n\n\n\n\n\n\n"
