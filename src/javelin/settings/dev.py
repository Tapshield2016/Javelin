from common import *
from kombu import Exchange, Queue

import djcelery
djcelery.setup_loader()

DATABASES = {
    'default': {
        #'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'javelin',
        'USER': 'javelin_user',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

INSTALLED_APPS += (
    'devserver',
)

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'beathan@gmail.com'
EMAIL_HOST_PASSWORD = 'blryunthuimaefkw'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# AWS
DYNAMO_DB_ACCESS_KEY_ID = 'AKIAJJX2VM346XUKRROA'
DYNAMO_DB_SECRET_ACCESS_KEY = '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'
DYNAMO_DB_CHAT_MESSAGES_TABLE = 'chat_messages_dev'
SQS_ALERT_QUEUE = 'alert_queue_dev'
SQS_ACCESS_KEY_ID = 'AKIAJSDRUWW6PPF2FWWA'
SQS_SECRET_ACCESS_KEY = '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'

# celery
BROKER_URL = "sqs://%s:%s@sqs.us-east-1.amazonaws.com/175861827001/"\
    % (SQS_ACCESS_KEY_ID, SQS_SECRET_ACCESS_KEY)
CELERY_DEFAULT_QUEUE = SQS_ALERT_QUEUE
CELERY_ROUTES = {
    'core.tasks.get_new_alerts': {
        'queue': SQS_ALERT_QUEUE,
        'routing_key': 'core.get_new_alerts',
    },
}
