from boto.exception import JSONResponseError

from django.conf import settings
from django.core.management.base import BaseCommand

from core.aws.dynamodb import DynamoDBManager


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            dynamo_db = DynamoDBManager()
            dynamo_db.create_table(\
                settings.DYNAMO_DB_CHAT_MESSAGES_TABLE, 5, 5)
        except JSONResponseError, e:
            print e

