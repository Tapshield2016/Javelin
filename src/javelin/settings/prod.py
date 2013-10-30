from common import *


DEBUG = False
TEMPLATE_DEBUG = DEBUG

#CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
#        'LOCATION': '',
#    }
#}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

# django-storages
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_ACCESS_KEY_ID = 'AKIAJHIUM7YWZW2T2YIA'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'media.tapshield.com'
AWS_HEADERS = {
    'Expires': 'Thu, 15 Apr 2030 20:00:00 GMT',
    'Cache-Control': 'max-age=86400',
}

# AWS
DYNAMO_DB_ACCESS_KEY_ID = 'AKIAJ34SY3EAOK6STBBA'
DYNAMO_DB_SECRET_ACCESS_KEY = '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'
DYNAMO_DB_CHAT_MESSAGES_TABLE ='chat_messages_prod'
SQS_ALERT_QUEUE = 'alert_queue_prod'
SQS_ACCESS_KEY_ID = 'AKIAJDLBPGLRJA4MOMVQ'
SQS_SECRET_ACCESS_KEY = '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'
