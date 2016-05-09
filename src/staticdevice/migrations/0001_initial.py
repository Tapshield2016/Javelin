# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-08 06:56
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('agency', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StaticDevice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.SlugField(help_text='Unique identifier (e.g. serial number)', max_length=255, unique=True)),
                ('type', models.CharField(blank=True, default='Emergency Phone', help_text='Model number or device type', max_length=255, null=True)),
                ('description', models.CharField(blank=True, help_text='(Auto-set if left empty by lat & lon Google Maps geocoder) Human readable identifier denoting location (e.g. building, street, landmark, etc.)', max_length=255, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('location_point', django.contrib.gis.db.models.fields.PointField(blank=True, geography=True, help_text='(Auto-set by lat & lon) Coordinate point used by geoDjango for queryingNote: The lat & lon is reversed to conform to a coordinate plane', null=True, srid=4326)),
                ('agency', models.ForeignKey(blank=True, help_text='(Auto-set if left empty by lat & lon to nearest within 10 miles) Who should receive the alert?', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='StaticDevice', to='agency.Agency')),
                ('user', models.ForeignKey(blank=True, help_text='Will be used in the future to limit edit/updated permissions to a particular authorization token', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'core_staticdevice',
            },
        ),
    ]