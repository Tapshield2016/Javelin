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
