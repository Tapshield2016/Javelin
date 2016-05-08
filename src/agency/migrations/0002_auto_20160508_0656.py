# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-08 06:56
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('agency', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='agency',
            name='agency_point_of_contact',
            field=models.ForeignKey(blank=True, help_text='This will be the person with full account access.  Edit all settings, change/add payment, add/remove dispatchers, etc.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='agency_point_of_contact', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='agency',
            name='branding',
            field=models.ForeignKey(blank=True, help_text='Internal UI elements for OEM partners', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='branding_theme', to='agency.Theme'),
        ),
        migrations.AddField(
            model_name='agency',
            name='theme',
            field=models.ForeignKey(blank=True, help_text='UI elements related to agency', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agency_theme', to='agency.Theme'),
        ),
    ]
