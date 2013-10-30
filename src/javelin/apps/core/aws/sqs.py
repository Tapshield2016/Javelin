from django.conf import settings

from boto.dynamodb2 import connect_to_region
from boto.dynamodb2.fields import HashKey, RangeKey, KeysOnlyIndex, AllIndex
from boto.dynamodb2.layer1 import DynamoDBConnection
from boto.dynamodb2.table import Table
from boto.dynamodb2.types import NUMBER


def create_connection():
    #if settings.DEBUG:
    #    return DynamoDBConnection(
    #        aws_access_key_id=settings.DYNAMO_DB_ACCESS_KEY_ID,
    #        aws_secret_access_key=settings.DYNAMO_DB_SECRET_ACCESS_KEY,
    #        host='0.0.0.0', port=7819)
    #else:
    return connect_to_region(\
        'us-east-1',
        aws_access_key_id=settings.DYNAMO_DB_ACCESS_KEY_ID,
        aws_secret_access_key=settings.DYNAMO_DB_SECRET_ACCESS_KEY)

def create_table(table_name, read_throughput, write_throughput):
    chat_messages = Table.create(table_name,
            connection=create_connection(),
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

def get_table(table_name):
    return Table(table_name, connection=create_connection())

def save_item_to_table(table_name, data):
    table = get_table(table_name)
    table.put_item(data=data)
