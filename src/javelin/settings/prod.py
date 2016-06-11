from common import *


DEBUG = False
TEMPLATE_DEBUG = DEBUG
WSGI_APPLICATION = 'javelin.wsgi.prod.application'

ALLOWED_HOSTS = ['*',]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
        'LOCATION': 'prodapicache.jgh2zp.cfg.use1.cache.amazonaws.com:11211',
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'javelin',
        'USER': 'javelin_user',
        'PASSWORD': '26947&83764w',
        'HOST': 'productionapi.cktvftiv8rvh.us-east-1.rds.amazonaws.com',
        'PORT': '5432',
    }
}

INSTALLED_APPS += (
    'gunicorn',
)

EMAIL_BACKEND = 'django_ses.SESBackend'
DEFAULT_FROM_EMAIL = 'TapShield <noreply@tapshield.com>'
SERVER_EMAIL = 'TapShield <noreply@tapshield.com>'

# django-storages
#DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
#STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
# AWS_ACCESS_KEY_ID = 'AKIAJHIUM7YWZW2T2YIA'
# AWS_SECRET_ACCESS_KEY = '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'
#AWS_STORAGE_BUCKET_NAME = 'static.tapshield.com'
#AWS_HEADERS = {
#    'Expires': 'Thu, 15 Apr 2030 20:00:00 GMT',
#    'Cache-Control': 'max-age=86400',
#}
#AWS_S3_SECURE_URLS = False
#STATIC_URL = 'http://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
#MEDIA_URL = 'http://%s/' % AWS_STORAGE_BUCKET_NAME

# django-storages
AWS_ACCESS_KEY_ID = 'AKIAJHIUM7YWZW2T2YIA'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'media.tapshield.com'
AWS_HEADERS = {
   'Expires': 'Thu, 15 Apr 2030 20:00:00 GMT',
   'Cache-Control': 'max-age=86400',
}
AWS_S3_BUCKET_URL = 'https://s3.amazonaws.com/%s/' % AWS_STORAGE_BUCKET_NAME
DEFAULT_BUCKET = AWS_STORAGE_BUCKET_NAME
USE_AMAZON_S3 = False

# AWS
DYNAMO_DB_ACCESS_KEY_ID = 'AKIAJ34SY3EAOK6STBBA'
DYNAMO_DB_SECRET_ACCESS_KEY = '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'
DYNAMO_DB_CHAT_MESSAGES_TABLE ='chat_messages_prod'

S3_ACCESS_KEY_ID = 'AKIAJHIUM7YWZW2T2YIA'
S3_SECRET_ACCESS_KEY = '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'

AWS_SES_ACCESS_KEY_ID = 'AKIAIO6P7N3P5KQFJIEQ'
AWS_SES_SECRET_ACCESS_KEY = '4IB6fssw4srhK7bWYrQZSVlqgMtHpb4NEh9QA0TJ'
AWS_SES_AUTO_THROTTLE = 1 # limiting factor on email sending, e.g. this will send the allowed number of emails per second as specified by SES, currently 5 emails per second. Setting to 0.5 would mean no more than 2.5 emails per second.

SQS_ALERT_QUEUE = 'alert_queue_prod'
SQS_ACCESS_KEY_ID = 'AKIAJDLBPGLRJA4MOMVQ'
SQS_SECRET_ACCESS_KEY = '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'

SNS_ACCESS_KEY_ID = 'AKIAI4LHPYPSGUMWIBLA'
SNS_SECRET_ACCESS_KEY = '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'
SNS_IOS_PLATFORM = 'APNS'
SNS_IOS_ARN = 'arn:aws:sns:us-east-1:175861827001:app/APNS/TapShield-iOS-Prod'
SNS_ANDROID_ARN = 'arn:aws:sns:us-east-1:175861827001:app/GCM/TapShield-Android-Prod'
SNS_ANDROID_PLATFORM = 'GCM'
SNS_ENDPOINT_QUEUE = 'endpoint_creation_queue_prod'

SNS_APP_ENDPOINTS = {
    "I": "APNS",
    "A": "GCM",
}

# celery
BROKER_URL = "sqs://%s:%s@sqs.us-east-1.amazonaws.com/175861827001/"\
    % (SQS_ACCESS_KEY_ID, SQS_SECRET_ACCESS_KEY)
CELERY_DEFAULT_QUEUE = SQS_ALERT_QUEUE

# compressor
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
#COMPRESS_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
#COMPRESS_URL = STATIC_URL

# twilio
TWILIO_ACCOUNT_SID = 'AC16b20300998d261efefb490dbc4a6302'
TWILIO_AUTH_TOKEN = '560b03d57aa563661444e63f0f7527e8'
TWILIO_APP_SID = 'AP534328fb5b4b0ea201cb32e40822316b'
TWILIO_SMS_FROM_NUMBER = '+18778296008'
TWILIO_SMS_VERIFICATION_FROM_NUMBER = '+14075455729'

# Shield Command
SHIELD_COMMAND_API_VERSION = "v1"
