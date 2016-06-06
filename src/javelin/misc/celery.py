from __future__ import absolute_import

import os
import sys

from celery import Celery

from django.conf import settings

sys.path.append('/srv/www/javelin/src')


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'javelin.settings.prod')

app = Celery('javelin')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
