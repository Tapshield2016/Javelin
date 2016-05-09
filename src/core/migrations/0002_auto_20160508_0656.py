# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-08 06:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('staticdevice', '0001_initial'),
        ('auth', '0007_alter_validators_add_error_messages'),
        ('agency', '0002_auto_20160508_0656'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='alert',
            name='static_device',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='static_device', to='staticdevice.StaticDevice'),
        ),
        migrations.AddField(
            model_name='agencyuser',
            name='agency',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='agency.Agency'),
        ),
        migrations.AddField(
            model_name='agencyuser',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='agencyuser',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]