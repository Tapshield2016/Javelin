from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models


class Agency(models.Model):
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255)
    dispatcher_phone_number = models.CharField(max_length=24)    
    agency_boundaries = models.MultiPolygonField()
    agency_center_latitude = models.FloatField()
    agency_center_longitude = models.FloatField()

    objects = models.Manager()
    geo = models.GeoManager()

    class Meta:
        verbose_name_plural = "Agencies"

    def __unicode__(self):
        return self.name


class AgencyUser(AbstractUser):
    agency = models.ForeignKey('Agency', null=True, blank=True)
    phone_number = models.CharField(max_length=24)
    disarm_code = models.CharField(max_length=10)
    email_verified = models.BooleanField(default=False)
    phone_number_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username',]

AgencyUser._meta.get_field_by_name('email')[0]._unique=True


class UserProfile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
