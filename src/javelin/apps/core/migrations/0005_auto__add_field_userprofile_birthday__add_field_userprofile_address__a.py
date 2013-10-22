# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'UserProfile.birthday'
        db.add_column(u'core_userprofile', 'birthday',
                      self.gf('django.db.models.fields.DateField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.address'
        db.add_column(u'core_userprofile', 'address',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.hair_color'
        db.add_column(u'core_userprofile', 'hair_color',
                      self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.gender'
        db.add_column(u'core_userprofile', 'gender',
                      self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.race'
        db.add_column(u'core_userprofile', 'race',
                      self.gf('django.db.models.fields.CharField')(max_length=3, null=True, blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.height'
        db.add_column(u'core_userprofile', 'height',
                      self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.weight'
        db.add_column(u'core_userprofile', 'weight',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'UserProfile.known_allergies'
        db.add_column(u'core_userprofile', 'known_allergies',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.medications'
        db.add_column(u'core_userprofile', 'medications',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.emergency_contact_first_name'
        db.add_column(u'core_userprofile', 'emergency_contact_first_name',
                      self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.emergency_contact_last_name'
        db.add_column(u'core_userprofile', 'emergency_contact_last_name',
                      self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.emergency_contact_phone_number'
        db.add_column(u'core_userprofile', 'emergency_contact_phone_number',
                      self.gf('django.db.models.fields.CharField')(max_length=24, null=True, blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.emergency_contact_relationship'
        db.add_column(u'core_userprofile', 'emergency_contact_relationship',
                      self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'UserProfile.birthday'
        db.delete_column(u'core_userprofile', 'birthday')

        # Deleting field 'UserProfile.address'
        db.delete_column(u'core_userprofile', 'address')

        # Deleting field 'UserProfile.hair_color'
        db.delete_column(u'core_userprofile', 'hair_color')

        # Deleting field 'UserProfile.gender'
        db.delete_column(u'core_userprofile', 'gender')

        # Deleting field 'UserProfile.race'
        db.delete_column(u'core_userprofile', 'race')

        # Deleting field 'UserProfile.height'
        db.delete_column(u'core_userprofile', 'height')

        # Deleting field 'UserProfile.weight'
        db.delete_column(u'core_userprofile', 'weight')

        # Deleting field 'UserProfile.known_allergies'
        db.delete_column(u'core_userprofile', 'known_allergies')

        # Deleting field 'UserProfile.medications'
        db.delete_column(u'core_userprofile', 'medications')

        # Deleting field 'UserProfile.emergency_contact_first_name'
        db.delete_column(u'core_userprofile', 'emergency_contact_first_name')

        # Deleting field 'UserProfile.emergency_contact_last_name'
        db.delete_column(u'core_userprofile', 'emergency_contact_last_name')

        # Deleting field 'UserProfile.emergency_contact_phone_number'
        db.delete_column(u'core_userprofile', 'emergency_contact_phone_number')

        # Deleting field 'UserProfile.emergency_contact_relationship'
        db.delete_column(u'core_userprofile', 'emergency_contact_relationship')


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
            'agency_boundaries': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {}),
            'agency_center_latitude': ('django.db.models.fields.FloatField', [], {}),
            'agency_center_longitude': ('django.db.models.fields.FloatField', [], {}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'dispatcher_phone_number': ('django.db.models.fields.CharField', [], {'max_length': '24'}),
            'dispatcher_schedule_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'dispatcher_schedule_start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'dispatcher_secondary_phone_number': ('django.db.models.fields.CharField', [], {'max_length': '24', 'null': 'True', 'blank': 'True'}),
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'core.agencyuser': {
            'Meta': {'object_name': 'AgencyUser'},
            'agency': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Agency']", 'null': 'True', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'disarm_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75', 'blank': 'True'}),
            'email_verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '24'}),
            'phone_number_verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
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
            'race': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.AgencyUser']"}),
            'weight': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['core']