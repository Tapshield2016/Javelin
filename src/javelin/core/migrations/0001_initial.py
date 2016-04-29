# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Agency'
        db.create_table(u'core_agency', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('domain', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('agency_point_of_contact', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='agency_point_of_contact', null=True, to=orm['core.AgencyUser'])),
            ('dispatcher_phone_number', self.gf('django.db.models.fields.CharField')(max_length=24)),
            ('dispatcher_secondary_phone_number', self.gf('django.db.models.fields.CharField')(max_length=24, null=True, blank=True)),
            ('dispatcher_schedule_start', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('dispatcher_schedule_end', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('agency_boundaries', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('agency_center_latitude', self.gf('django.db.models.fields.FloatField')()),
            ('agency_center_longitude', self.gf('django.db.models.fields.FloatField')()),
            ('default_map_zoom_level', self.gf('django.db.models.fields.PositiveIntegerField')(default=15)),
            ('alert_completed_message', self.gf('django.db.models.fields.TextField')(default='Thank you for using TapShield. Please enter disarm code to complete this session.', null=True, blank=True)),
            ('sns_primary_topic_arn', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['Agency'])

        # Adding model 'Alert'
        db.create_table(u'core_alert', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('agency', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Agency'])),
            ('agency_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='alert_agency_user', to=orm['core.AgencyUser'])),
            ('agency_dispatcher', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='alert_agency_dispatcher', null=True, to=orm['core.AgencyUser'])),
            ('accepted_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('completed_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('disarmed_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('pending_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='N', max_length=1)),
            ('initiated_by', self.gf('django.db.models.fields.CharField')(default='E', max_length=2)),
            ('user_notified_of_receipt', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'core', ['Alert'])

        # Adding model 'AlertLocation'
        db.create_table(u'core_alertlocation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('alert', self.gf('django.db.models.fields.related.ForeignKey')(related_name='locations', to=orm['core.Alert'])),
            ('accuracy', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('altitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('latitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['AlertLocation'])

        # Adding model 'MassAlert'
        db.create_table(u'core_massalert', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('agency', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Agency'])),
            ('agency_dispatcher', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.AgencyUser'])),
            ('message', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'core', ['MassAlert'])

        # Adding model 'AgencyUser'
        db.create_table(u'core_agencyuser', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('is_superuser', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(unique=True, max_length=75, blank=True)),
            ('is_staff', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date_joined', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('agency', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Agency'], null=True, blank=True)),
            ('phone_number', self.gf('django.db.models.fields.CharField')(max_length=24)),
            ('phone_number_verification_code', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('phone_number_verified', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('disarm_code', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('email_verified', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('device_token', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('device_endpoint_arn', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('device_type', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['AgencyUser'])

        # Adding M2M table for field groups on 'AgencyUser'
        m2m_table_name = db.shorten_name(u'core_agencyuser_groups')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('agencyuser', models.ForeignKey(orm[u'core.agencyuser'], null=False)),
            ('group', models.ForeignKey(orm[u'auth.group'], null=False))
        ))
        db.create_unique(m2m_table_name, ['agencyuser_id', 'group_id'])

        # Adding M2M table for field user_permissions on 'AgencyUser'
        m2m_table_name = db.shorten_name(u'core_agencyuser_user_permissions')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('agencyuser', models.ForeignKey(orm[u'core.agencyuser'], null=False)),
            ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
        ))
        db.create_unique(m2m_table_name, ['agencyuser_id', 'permission_id'])

        # Adding model 'UserProfile'
        db.create_table(u'core_userprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.AgencyUser'], unique=True)),
            ('birthday', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('hair_color', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('race', self.gf('django.db.models.fields.CharField')(max_length=3, null=True, blank=True)),
            ('height', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('weight', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, null=True, blank=True)),
            ('known_allergies', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('medications', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('emergency_contact_first_name', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('emergency_contact_last_name', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('emergency_contact_phone_number', self.gf('django.db.models.fields.CharField')(max_length=24, null=True, blank=True)),
            ('emergency_contact_relationship', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('profile_image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('profile_image_url', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['UserProfile'])

        # Adding model 'ChatMessage'
        db.create_table(u'core_chatmessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('alert', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Alert'])),
            ('sender', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.AgencyUser'])),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('message_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('message_sent_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'core', ['ChatMessage'])


    def backwards(self, orm):
        # Deleting model 'Agency'
        db.delete_table(u'core_agency')

        # Deleting model 'Alert'
        db.delete_table(u'core_alert')

        # Deleting model 'AlertLocation'
        db.delete_table(u'core_alertlocation')

        # Deleting model 'MassAlert'
        db.delete_table(u'core_massalert')

        # Deleting model 'AgencyUser'
        db.delete_table(u'core_agencyuser')

        # Removing M2M table for field groups on 'AgencyUser'
        db.delete_table(db.shorten_name(u'core_agencyuser_groups'))

        # Removing M2M table for field user_permissions on 'AgencyUser'
        db.delete_table(db.shorten_name(u'core_agencyuser_user_permissions'))

        # Deleting model 'UserProfile'
        db.delete_table(u'core_userprofile')

        # Deleting model 'ChatMessage'
        db.delete_table(u'core_chatmessage')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'core.agency': {
            'Meta': {'object_name': 'Agency'},
            'agency_boundaries': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'agency_center_latitude': ('django.db.models.fields.FloatField', [], {}),
            'agency_center_longitude': ('django.db.models.fields.FloatField', [], {}),
            'agency_point_of_contact': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'agency_point_of_contact'", 'null': 'True', 'to': u"orm['core.AgencyUser']"}),
            'alert_completed_message': ('django.db.models.fields.TextField', [], {'default': "'Thank you for using TapShield. Please enter disarm code to complete this session.'", 'null': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'default_map_zoom_level': ('django.db.models.fields.PositiveIntegerField', [], {'default': '15'}),
            'dispatcher_phone_number': ('django.db.models.fields.CharField', [], {'max_length': '24'}),
            'dispatcher_schedule_end': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'dispatcher_schedule_start': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'dispatcher_secondary_phone_number': ('django.db.models.fields.CharField', [], {'max_length': '24', 'null': 'True', 'blank': 'True'}),
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sns_primary_topic_arn': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'core.agencyuser': {
            'Meta': {'object_name': 'AgencyUser'},
            'agency': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Agency']", 'null': 'True', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'device_endpoint_arn': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'device_token': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'device_type': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'disarm_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75', 'blank': 'True'}),
            'email_verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '24'}),
            'phone_number_verification_code': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'phone_number_verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'core.alert': {
            'Meta': {'ordering': "['-creation_date']", 'object_name': 'Alert'},
            'accepted_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'agency': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Agency']"}),
            'agency_dispatcher': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'alert_agency_dispatcher'", 'null': 'True', 'to': u"orm['core.AgencyUser']"}),
            'agency_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'alert_agency_user'", 'to': u"orm['core.AgencyUser']"}),
            'completed_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'disarmed_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initiated_by': ('django.db.models.fields.CharField', [], {'default': "'E'", 'max_length': '2'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'pending_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '1'}),
            'user_notified_of_receipt': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'core.alertlocation': {
            'Meta': {'ordering': "['-creation_date']", 'object_name': 'AlertLocation'},
            'accuracy': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'alert': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'locations'", 'to': u"orm['core.Alert']"}),
            'altitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        u'core.chatmessage': {
            'Meta': {'ordering': "['message_sent_time']", 'object_name': 'ChatMessage'},
            'alert': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Alert']"}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'message_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'message_sent_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.AgencyUser']"})
        },
        u'core.massalert': {
            'Meta': {'ordering': "['-creation_date']", 'object_name': 'MassAlert'},
            'agency': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Agency']"}),
            'agency_dispatcher': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.AgencyUser']"}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {})
        },
        u'core.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'birthday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'emergency_contact_first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'emergency_contact_last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'emergency_contact_phone_number': ('django.db.models.fields.CharField', [], {'max_length': '24', 'null': 'True', 'blank': 'True'}),
            'emergency_contact_relationship': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'hair_color': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'known_allergies': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'medications': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'profile_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'profile_image_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'race': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.AgencyUser']", 'unique': 'True'}),
            'weight': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['core']