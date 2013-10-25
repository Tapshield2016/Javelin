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
