from django.conf import settings

from boto.dynamodb2 import connect_to_region
from boto.dynamodb2.fields import HashKey, RangeKey, KeysOnlyIndex, AllIndex
from boto.dynamodb2.layer1 import DynamoDBConnection
from boto.dynamodb2.table import Table
from boto.dynamodb2.types import NUMBER


class DynamoDBManager(object):

    def __init__(self):
        self.connection = self.create_connection()

    def create_connection(self):
        return connect_to_region(\
            'us-east-1',
            aws_access_key_id=settings.DYNAMO_DB_ACCESS_KEY_ID,
            aws_secret_access_key=settings.DYNAMO_DB_SECRET_ACCESS_KEY)

    def create_table(self, table_name, read_throughput, write_throughput):
        chat_messages =\
            Table.create(table_name,
                         connection=self.connection,
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
        return chat_messages

    def get_table(self, table_name):
        return Table(table_name, connection=self.connection)

    def save_item_to_table(self, table_name, data):
        table = self.get_table(table_name)
        table.put_item(data=data)

    def get_messages_for_alert(self, alert_id):
        messages = []
        table = self.get_table(settings.DYNAMO_DB_CHAT_MESSAGES_TABLE)
        results = table.query(alert_id__eq=int(alert_id))
        for res in results:
            messages.append(dict([(key, val) for key, val in res.items()]))
        return messages

    def get_messages_for_alert_since_time(self, alert_id, timestamp):
        messages = []
        timestamp = float(timestamp)
        table = self.get_table(settings.DYNAMO_DB_CHAT_MESSAGES_TABLE)
        results = table.query(alert_id__eq=int(alert_id),
                              timestamp__gt=timestamp)
        for res in results:
            messages.append(dict([(key, val) for key, val in res.items()]))
        return messages
