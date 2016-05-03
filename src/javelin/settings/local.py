from common import *

ALLOWED_HOSTS = ['127.0.0.1:8000']


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'prod_copy',
        'USER': '',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '5432',
    },
}

INSTALLED_APPS += (
    #'corsheaders',
    #'devserver',
    'rest_framework_swagger',
    #'debug_toolbar',
    # 'gunicorn',
)

MIDDLEWARE_CLASSES += (
    #'corsheaders.middleware.CorsMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INTERNAL_IPS = ('127.0.0.1',)

EMAIL_BACKEND = 'django_ses.SESBackend'
DEFAULT_FROM_EMAIL = 'TapShield Dev <noreply@tapshield.com>'
SERVER_EMAIL = 'TapShield Dev <noreply@tapshield.com>'

# django-storages
AWS_ACCESS_KEY_ID = 'AKIAJHIUM7YWZW2T2YIA'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'dev.media.tapshield.com'
AWS_HEADERS = {
   'Expires': 'Thu, 15 Apr 2030 20:00:00 GMT',
   'Cache-Control': 'max-age=86400',
}
AWS_S3_BUCKET_URL = 'https://s3.amazonaws.com/%s/' % AWS_STORAGE_BUCKET_NAME
DEFAULT_BUCKET = AWS_STORAGE_BUCKET_NAME
USE_AMAZON_S3 = False

# AWS
DYNAMO_DB_ACCESS_KEY_ID = 'AKIAJJX2VM346XUKRROA'
DYNAMO_DB_SECRET_ACCESS_KEY = '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'
DYNAMO_DB_CHAT_MESSAGES_TABLE = 'chat_messages_dev'

S3_ACCESS_KEY_ID = 'AKIAJHIUM7YWZW2T2YIA'
S3_SECRET_ACCESS_KEY = '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'

AWS_SES_ACCESS_KEY_ID = 'AKIAJV725S6GDYWDLJYA'
AWS_SES_SECRET_ACCESS_KEY = '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'

SQS_ALERT_QUEUE = 'alert_queue_dev'
SQS_ACCESS_KEY_ID = 'AKIAJSDRUWW6PPF2FWWA'
SQS_SECRET_ACCESS_KEY = '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'

SNS_ACCESS_KEY_ID = 'AKIAITQVGREAX47VJCYQ'
SNS_SECRET_ACCESS_KEY = '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'
SNS_IOS_ARN = 'arn:aws:sns:us-east-1:175861827001:app/APNS_SANDBOX/TapShield-iOS-Dev'
SNS_IOS_PLATFORM = 'APNS_SANDBOX'
SNS_ANDROID_ARN = 'arn:aws:sns:us-east-1:175861827001:app/GCM/TapShield-Android-Dev'
SNS_ANDROID_PLATFORM = 'GCM'
SNS_ENDPOINT_QUEUE = 'endpoint_creation_queue_dev'

SNS_APP_ENDPOINTS = {
    "I": "APNS_SANDBOX",
    "A": "GCM",
}

# celery
BROKER_URL = "sqs://%s:%s@sqs.us-east-1.amazonaws.com/175861827001/"\
    % (SQS_ACCESS_KEY_ID, SQS_SECRET_ACCESS_KEY)
CELERY_DEFAULT_QUEUE = SQS_ALERT_QUEUE

# twilio
#TWILIO_ACCOUNT_SID = 'ACbadf905d23464a0afc0ed64b80e8def1'
TWILIO_ACCOUNT_SID = 'AC16b20300998d261efefb490dbc4a6302'
#TWILIO_AUTH_TOKEN = '86aeeaac35d98f7243b30768f6f51824'
TWILIO_AUTH_TOKEN = '560b03d57aa563661444e63f0f7527e8'
TWILIO_APP_SID = 'AP299c4eeef7fb59999a8258140fc3d8a2'
TWILIO_SMS_FROM_NUMBER = '+18778296008'
TWILIO_SMS_VERIFICATION_FROM_NUMBER = '+14075455729'

# cors
CORS_ORIGIN_ALLOW_ALL = True

# Shield Command
SHIELD_COMMAND_API_VERSION = "v1"

# compressor
COMPRESS_ENABLED = False
