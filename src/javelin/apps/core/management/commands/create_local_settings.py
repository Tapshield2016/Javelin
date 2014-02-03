import os.path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        local_settings_path =\
            "%s/settings/local_settings.py" % settings.PROJECT_DIR
        local_settings_initial = """
# Override settings for local development so as not to clash
# with dev.tapshield.com
DYNAMO_DB_CHAT_MESSAGES_TABLE = 'local_dev_chat_messages'
SQS_ALERT_QUEUE = 'local_dev_alert_queue'
CELERY_DEFAULT_QUEUE = SQS_ALERT_QUEUE
DEFAULT_FROM_EMAIL = 'Local TapShield Dev <noreply@tapshield.com>'
"""
        fp = open(local_settings_path, 'w')
        fp.write(local_settings_initial)
        fp.close()
