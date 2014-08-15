# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'EmailAddress'
        db.create_table('emailmgr_emailaddress', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='secondary_email', to=orm['core.AgencyUser'])),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('is_primary', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('identifier', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
        ))
        db.send_create_signal('emailmgr', ['EmailAddress'])

        # Adding unique constraint on 'EmailAddress', fields ['user', 'email']
        db.create_unique('emailmgr_emailaddress', ['user_id', 'email'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'EmailAddress', fields ['user', 'email']
        db.delete_unique('emailmgr_emailaddress', ['user_id', 'email'])

        # Deleting model 'EmailAddress'
        db.delete_table('emailmgr_emailaddress')


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
                u'core.agency': {
            'Meta': {'ordering': "['name']", 'object_name': 'Agency'},
            'agency_alternate_logo': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'agency_boundaries': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'agency_center_from_boundaries': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'agency_center_latitude': ('django.db.models.fields.FloatField', [], {}),
            'agency_center_longitude': ('django.db.models.fields.FloatField', [], {}),
            'agency_center_point': ('django.contrib.gis.db.models.fields.PointField', [], {'blank': 'True', 'null': 'True', 'geography': 'True'}),
            'agency_radius': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'agency_info_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'agency_logo': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'agency_point_of_contact': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'agency_point_of_contact'", 'null': 'True', 'to': u"orm['core.AgencyUser']"}),
            'agency_rss_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'agency_small_logo': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'agency_theme': ('django.db.models.fields.TextField', [], {'default': "'{}'", 'null': 'True', 'blank': 'True'}),
            'alert_completed_message': ('django.db.models.fields.TextField', [], {'default': "'Thank you for using TapShield. Please enter disarm code to complete this session.'", 'null': 'True', 'blank': 'True'}),
            'alert_mode_name': ('django.db.models.fields.CharField', [], {'default': "'Emergency'", 'max_length': '24'}),
            'alert_received_message': ('django.db.models.fields.CharField', [], {'default': "'The authorities have been notified.'", 'max_length': '255'}),
            'chat_autoresponder_message': ('django.db.models.fields.TextField', [], {'default': "'Due to high volume, we are currently experiencing delays. Call 911 if you require immediate assistance.'", 'null': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'default_map_zoom_level': ('django.db.models.fields.PositiveIntegerField', [], {'default': '15'}),
            'dispatcher_phone_number': ('django.db.models.fields.CharField', [], {'max_length': '24'}),
            'dispatcher_schedule_end': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'dispatcher_schedule_start': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'dispatcher_secondary_phone_number': ('django.db.models.fields.CharField', [], {'max_length': '24', 'null': 'True', 'blank': 'True'}),
            'display_command_alert': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'enable_chat_autoresponder': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'enable_user_location_requests': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'launch_call_to_dispatcher_on_alert': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'loop_alert_sound': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'require_domain_emails': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_agency_name_in_app_navbar': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sns_primary_topic_arn': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'core.agencyuser': {
            'Meta': {'object_name': 'AgencyUser'},
            'agency': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Agency']", 'null': 'True', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'device_endpoint_arn': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'device_token': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'device_type': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'disarm_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
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
            'last_reported_latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'last_reported_longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'last_reported_point': ('django.contrib.gis.db.models.fields.PointField', [], {'blank': 'True', 'null': 'True', 'geography': 'True'}),
            'last_reported_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'notify_entourage_on_alert': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '24', 'null': 'True', 'blank': 'True'}),
            'phone_number_verification_code': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'phone_number_verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user_declined_push_notifications': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user_logged_in_via_social': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'emailmgr.emailaddress': {
            'Meta': {'unique_together': "(('user', 'email'),)", 'object_name': 'EmailAddress'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'emailaddress'", 'to': u"orm['core.Agency']"})
        }
    }

    complete_apps = ['emailmgr']
