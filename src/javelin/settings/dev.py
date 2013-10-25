from common import *


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
