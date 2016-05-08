# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-08 06:56
from __future__ import unicode_literals

import agency.models
import core.aws.s3_filefield
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Agency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('domain', models.CharField(default='tapshield.com', max_length=255)),
                ('dispatcher_phone_number', models.CharField(default='5555555555', max_length=24)),
                ('dispatcher_secondary_phone_number', models.CharField(blank=True, default='555', help_text='Defaults to 911 within apps unless specified', max_length=24, null=True)),
                ('dispatcher_schedule_start', models.TimeField(blank=True, null=True)),
                ('dispatcher_schedule_end', models.TimeField(blank=True, null=True)),
                ('agency_boundaries', models.TextField(blank=True, help_text='For multiple boundaries use Regions', null=True)),
                ('agency_center_from_boundaries', models.BooleanField(default=True)),
                ('agency_center_latitude', models.FloatField(default=0)),
                ('agency_center_longitude', models.FloatField(default=0)),
                ('agency_center_point', django.contrib.gis.db.models.fields.PointField(blank=True, geography=True, null=True, srid=4326)),
                ('agency_radius', models.FloatField(default=0)),
                ('default_map_zoom_level', models.PositiveIntegerField(default=15)),
                ('alert_mode_name', models.CharField(default='Campus Police', help_text="This can be changed on the wishes of the organization to be 'Police', 'Alert', etc.", max_length=24)),
                ('alert_received_message', models.CharField(default='The authorities have been notified.', max_length=255)),
                ('alert_completed_message', models.TextField(blank=True, default='Thank you for using TapShield. Your alert session was completed by dispatcher <first_name>.', null=True)),
                ('sns_primary_topic_arn', models.CharField(blank=True, max_length=255, null=True)),
                ('require_domain_emails', models.BooleanField(default=True)),
                ('display_command_alert', models.BooleanField(default=True)),
                ('loop_alert_sound', models.BooleanField(default=True)),
                ('launch_call_to_dispatcher_on_alert', models.BooleanField(default=True, help_text="When a mobile user begins an alert, immediately launch a VoIP call to the primary dispatcher number for the user's organization.")),
                ('show_agency_name_in_app_navbar', models.BooleanField(default=True)),
                ('enable_chat_autoresponder', models.BooleanField(default=False, help_text='If enabled, please set the chat autoresponder message below if you wish to respond with something that differs from the default text.', verbose_name='enable chat auto-responder')),
                ('chat_autoresponder_message', models.TextField(blank=True, default='Due to high volume, we are currently experiencing delays. Call 911 if you require immediate assistance.', null=True, verbose_name='chat auto-responder message')),
                ('enable_user_location_requests', models.BooleanField(default=False, help_text="If enabled, this allows for Shield Command dispatchers to request the latest location from users belonging to the organization. This is accomplished by sending a push notification to the organization's SNS topic to prompt devices to send a location update in the background. This does not disturb the users.")),
                ('agency_logo', models.URLField(blank=True, help_text='Set the location of the standard agency logo.', null=True)),
                ('agency_alternate_logo', models.URLField(blank=True, help_text='This could be an inverted version of the standard logo or other differently colorized/formatted version.', null=True)),
                ('agency_small_logo', models.URLField(blank=True, help_text="This could be a truncated or minimized form of the logo, e.g. 'UF' versus the larger logo version.", null=True)),
                ('agency_theme', models.TextField(blank=True, default='{}', help_text='Use properly formatted JSON here to provide data as necessary.', null=True)),
                ('agency_info_url', models.CharField(blank=True, help_text='This could be a web page with important info pertaining to emergency situations', max_length=255, null=True)),
                ('agency_rss_url', models.CharField(blank=True, help_text='RSS feed for mass alerts already populated by the system in use', max_length=255, null=True)),
                ('spot_crime_days_visible', models.PositiveIntegerField(default=1)),
                ('hidden', models.BooleanField(default=True, help_text='Hide organization from query list. Apps will no be able to add until visible')),
                ('full_version', models.BooleanField(default=True, help_text='When checked all services will be made available')),
                ('no_alerts', models.BooleanField(default=False, help_text='Auto-checked when no alert types are available for internal use')),
                ('crime_reports_available', models.BooleanField(default=True)),
                ('emergency_call_available', models.BooleanField(default=True)),
                ('alert_available', models.BooleanField(default=True)),
                ('chat_available', models.BooleanField(default=True)),
                ('yank_available', models.BooleanField(default=True)),
                ('entourage_available', models.BooleanField(default=True)),
                ('static_device_available', models.BooleanField(default=True)),
                ('mass_alert_available', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['name'],
                'db_table': 'core_agency',
                'verbose_name_plural': 'Agencies',
            },
        ),
        migrations.CreateModel(
            name='ClosedDate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField(blank=True, null=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'core_closeddate',
            },
        ),
        migrations.CreateModel(
            name='DispatchCenter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('phone_number', models.CharField(max_length=24)),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dispatch_center', to='agency.Agency')),
            ],
            options={
                'db_table': 'core_dispatchcenter',
            },
        ),
        migrations.CreateModel(
            name='Period',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.CharField(choices=[('1', 'Sunday'), ('2', 'Monday'), ('3', 'Tuesday'), ('4', 'Wednesday'), ('5', 'Thursday'), ('6', 'Friday'), ('7', 'Saturday')], default='1', max_length=1)),
                ('open', models.TimeField(blank=True, null=True)),
                ('close', models.TimeField(blank=True, null=True)),
                ('dispatch_center', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='opening_hours', to='agency.DispatchCenter')),
            ],
            options={
                'ordering': ['day'],
                'db_table': 'core_period',
                'verbose_name': 'Period',
                'verbose_name_plural': 'Opening Hours',
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('boundaries', models.TextField(blank=True, null=True)),
                ('center_latitude', models.FloatField()),
                ('center_longitude', models.FloatField()),
                ('center_point', django.contrib.gis.db.models.fields.PointField(blank=True, geography=True, null=True, srid=4326)),
                ('radius', models.FloatField(default=0)),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='region', to='agency.Agency')),
                ('fallback_dispatch_center', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='fallback_dispatch_center', to='agency.DispatchCenter')),
                ('primary_dispatch_center', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='primary_dispatch_center', to='agency.DispatchCenter')),
                ('secondary_dispatch_center', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='secondary_dispatch_center', to='agency.DispatchCenter')),
            ],
            options={
                'db_table': 'core_region',
            },
        ),
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('primary_color', models.CharField(blank=True, help_text="Primary color of an organization's logo or color scheme", max_length=8, null=True)),
                ('secondary_color', models.CharField(blank=True, help_text="Secondary color of an organization's logo or color scheme", max_length=8, null=True)),
                ('alternate_color', models.CharField(blank=True, help_text='Alternate color, maybe something neutral such as white', max_length=8, null=True)),
                ('small_logo', core.aws.s3_filefield.S3EnabledImageField(blank=True, help_text="Truncated or minimized form of the logo, e.g. 'UF' versus the larger logo version for organization lists.", null=True, upload_to=agency.models.file_path)),
                ('navbar_logo', core.aws.s3_filefield.S3EnabledImageField(blank=True, help_text='For light background on home screen', null=True, upload_to=agency.models.file_path)),
                ('navbar_logo_alternate', core.aws.s3_filefield.S3EnabledImageField(blank=True, help_text='For dark background on alert screen', null=True, upload_to=agency.models.file_path)),
                ('map_overlay_logo', core.aws.s3_filefield.S3EnabledImageField(blank=True, help_text='Large logo for overlaying on map geofence', null=True, upload_to=agency.models.file_path)),
                ('shield_command_logo', core.aws.s3_filefield.S3EnabledImageField(blank=True, help_text='Logo re-sized for Shield Command. 10% top and bottom padding recommended', null=True, upload_to=agency.models.file_path)),
            ],
            options={
                'db_table': 'core_theme',
            },
        ),
        migrations.AddField(
            model_name='closeddate',
            name='dispatch_center',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='closed_date', to='agency.DispatchCenter'),
        ),
    ]
