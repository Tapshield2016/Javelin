# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-08 08:00
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('agency', '0003_auto_20160508_0723'),
    ]

    operations = [
        migrations.AddField(
            model_name='agency',
            name='dispatchers',
            field=models.ManyToManyField(related_name='agency_access', to=settings.AUTH_USER_MODEL),
        ),
    ]
