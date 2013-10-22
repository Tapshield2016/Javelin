from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models


class TimeStampedModel(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Agency(TimeStampedModel):
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255)
    dispatcher_phone_number = models.CharField(max_length=24)
    dispatcher_secondary_phone_number = models.CharField(max_length=24,
                                                         null=True, blank=True)
    dispatcher_schedule_start = models.DateTimeField(null=True, blank=True)
    dispatcher_schedule_end = models.DateTimeField(null=True, blank=True)
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
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

    HAIR_COLOR_CHOICES = (
        ('Y', 'Blonde'),
        ('BR', 'Brown'),
        ('BL', 'Black'),
        ('R', 'Red'),
        ('BA', 'Bald'),
        ('GR', 'Gray'),
    )

    RACE_CHOICES = (
        ('BA', 'Black/African Descent'),
        ('WC', 'White/Caucasian'),
        ('EI', 'East Indian'),
        ('AS', 'Asian'),
        ('LH', 'Latino/Hispanic'),
        ('ME', 'Middle Eastern'),
        ('PI', 'Pacific Islander'),
        ('NA', 'Native American'),
    )

    RELATIONSHIP_CHOICES = (
        ('F', 'Father'),
        ('M', 'Mother'),
        ('S', 'Spouse'),
        ('BF', 'Boyfriend'),
        ('GF', 'Girlfriend'),
        ('B', 'Brother'),
        ('S', 'Sister'),
        ('FR', 'Friend'),
        ('O', 'Other'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    birthday = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    hair_color = models.CharField(max_length=2, choices=HAIR_COLOR_CHOICES,
                                  null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES,
                              null=True, blank=True)
    race = models.CharField(max_length=3, choices=RACE_CHOICES,
                            null=True, blank=True)
    height = models.CharField(max_length=10, null=True, blank=True)
    weight = models.PositiveIntegerField(default=0, null=True, blank=True)
    known_allergies = models.TextField(null=True, blank=True)
    medications = models.TextField(null=True, blank=True)
    emergency_contact_first_name = models.CharField(max_length=30, null=True,
                                                    blank=True)
    emergency_contact_last_name = models.CharField(max_length=30, null=True,
                                                   blank=True)
    emergency_contact_phone_number = models.CharField(max_length=24,
                                                      null=True, blank=True)
    emergency_contact_relationship =\
        models.CharField(max_length=2, choices=RELATIONSHIP_CHOICES,
                         null=True, blank=True)
