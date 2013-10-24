from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from rest_framework.authtoken.models import Token


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
    dispatcher_schedule_start = models.TimeField(null=True, blank=True)
    dispatcher_schedule_end = models.TimeField(null=True, blank=True)
    agency_boundaries = models.MultiPolygonField()
    agency_center_latitude = models.FloatField()
    agency_center_longitude = models.FloatField()
    alert_completed_message = models.TextField(null=True, blank=True)

    objects = models.Manager()
    geo = models.GeoManager()

    class Meta:
        verbose_name_plural = "Agencies"

    def __unicode__(self):
        return self.name


class Alert(TimeStampedModel):
    STATUS_CHOICES = (
        ('A', 'Accepted'),
        ('C', 'Completed'),
        ('D', 'Disarmed'),
        ('N', 'New'),
        ('P', 'Pending'),
    )

    ALERT_INITIATED_BY_CHOICES = (
        ('C', 'Chat'),
        ('E', 'Emergency'),
        ('T', 'Timer'),
    )

    ALERT_CATEGORY = (
        ('GE', 'General'),
        ('ME', 'Medical'),
        ('FI', 'Fire'),
        ('AU', 'Auto'),
        ('DR', 'Drugs/Alcohol'),
        ('SA', 'Sexual Assault'),
        ('RO', 'Robbery'),
        ('SP', 'Suspicious Person'),
    )

    agency = models.ForeignKey('Agency')
    agency_user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    related_name="alert_agency_user")
    agency_dispatcher =\
        models.ForeignKey(settings.AUTH_USER_MODEL,
                          related_name="alert_agency_dispatcher")
    accepted_time = models.DateTimeField(null=True, blank=True)
    completed_time = models.DateTimeField(null=True, blank=True)
    disarmed_time = models.DateTimeField(null=True, blank=True)
    pending_time = models.DateTimeField(null=True, blank=True)
    location_accuracy = models.FloatField(null=True, blank=True)
    location_address =\
        models.CharField(max_length=255, null=True, blank=True)
    location_altitude = models.FloatField(null=True, blank=True)
    location_latitude = models.FloatField(null=True, blank=True)
    location_longitude = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES,
                              default='N')
    initiated_by = models.CharField(max_length=2,
                                    choices=ALERT_INITIATED_BY_CHOICES)

    def save(self, *args, **kwargs):
        super(Alert, self).save(*args, **kwargs)
        if self.status == 'C':
            try:
                profile = self.agency_user.get_profile()
                profile.delete()
            except UserProfile.DoesNotExist:
                pass

class MassAlert(TimeStampedModel):
    agency = models.ForeignKey('Agency')
    agency_dispatcher = models.ForeignKey(settings.AUTH_USER_MODEL)
    message = models.TextField()


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


class ChatMessage(TimeStampedModel):
    alert = models.ForeignKey('Alert')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL)
    message = models.TextField()


@receiver(pre_save, sender=AgencyUser)
def mark_new_user_inactive(sender, instance=None, *args, **kwargs):
    if instance.pk is None:
        instance.is_active = False


@receiver(post_save, sender=AgencyUser)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(post_save, sender=AgencyUser)
def verify_email_address(sender, instance=None, created=False, **kwargs):
    if created:
        # We'll want to fire off the verification process here
        pass
