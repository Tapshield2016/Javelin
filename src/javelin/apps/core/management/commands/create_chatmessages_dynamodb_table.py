from django.conf import settings
from django.core.management.base import BaseCommand

import boto.dynamodb2
from boto.dynamodb2.fields import HashKey, RangeKey, KeysOnlyIndex, AllIndex
from boto.dynamodb2.table import Table
from boto.dynamodb2.types import NUMBER

class Command(BaseCommand):

    def handle(self, *args, **options):
        self.create_table('chat_messages', 5, 5)

    def create_table(self, table_name, read_throughput, write_throughput):
        chat_messages = Table.create(table_name,
            connection=boto.dynamodb2.connect_to_region('us-east-1',
                aws_access_key_id=settings.DYNAMO_DB_ACCESS_KEY_ID,
                aws_secret_access_key=settings.DYNAMO_DB_SECRET_ACCESS_KEY,
            ),
            schema=[
                HashKey('alert_id', data_type=NUMBER),
                RangeKey('timestamp', data_type=NUMBER),
            ],
            throughput={
                'read': read_throughput,
                'write': write_throughput,
            },
            indexes=[
                AllIndex('MessageTimeIndex', parts=[
                        HashKey('alert_id'),
                        RangeKey('timestamp'),
                    ]),
            ]
        )
