from django.conf import settings
from django.core.management.base import BaseCommand

from core.aws import create_table


class Command(BaseCommand):

    def handle(self, *args, **options):
        create_table(settings.DYNAMO_DB_CHAT_MESSAGES_TABLE, 5, 5)
