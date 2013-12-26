import random

from datetime import datetime

import django.utils.timezone

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_delete, pre_save, post_save
from django.dispatch import receiver
from django.utils.text import slugify

from registration.signals import user_activated
from rest_framework.authtoken.models import Token

from managers import (ActiveAlertManager, InactiveAlertManager,
                      AcceptedAlertManager, CompletedAlertManager,
                      DisarmedAlertManager, NewAlertManager,
                      PendingAlertManager, InitiatedByChatAlertManager,
                      InitiatedByEmergencyAlertManager,
                      InitiatedByTimerAlertManager)


class TimeStampedModel(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Agency(TimeStampedModel):
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255)
    agency_point_of_contact =\
        models.ForeignKey(settings.AUTH_USER_MODEL,
                          related_name='agency_point_of_contact',
                          null=True, blank=True)
    dispatcher_phone_number = models.CharField(max_length=24)
    dispatcher_secondary_phone_number = models.CharField(max_length=24,
                                                         null=True, blank=True)
    dispatcher_schedule_start = models.TimeField(null=True, blank=True)
    dispatcher_schedule_end = models.TimeField(null=True, blank=True)
    agency_boundaries = models.TextField(null=True, blank=True)
    agency_center_latitude = models.FloatField()
    agency_center_longitude = models.FloatField()
    default_map_zoom_level = models.PositiveIntegerField(default=15)
    alert_completed_message = models.TextField(null=True, blank=True,
                                               default="Thank you for using TapShield. Please enter disarm code to complete this session.")
    sns_primary_topic_arn = models.CharField(max_length=255,
                                             null=True, blank=True)

    objects = models.Manager()

    class Meta:
        verbose_name_plural = "Agencies"

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        from tasks import create_agency_topic
        super(Agency, self).save(*args, **kwargs)
        if not self.sns_primary_topic_arn:
            create_agency_topic.delay(self.pk)


class Alert(TimeStampedModel):
    STATUS_CHOICES = (
        ('A', 'Accepted'),
        ('C', 'Completed'),
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
                          related_name="alert_agency_dispatcher",
                          blank=True, null=True)
    accepted_time = models.DateTimeField(null=True, blank=True)
    completed_time = models.DateTimeField(null=True, blank=True)
    disarmed_time = models.DateTimeField(null=True, blank=True)
    pending_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES,
                              default='N')
    initiated_by = models.CharField(max_length=2,
                                    choices=ALERT_INITIATED_BY_CHOICES,
                                    default='E')
    user_notified_of_receipt = models.BooleanField(default=False)

    objects = models.Manager()
    active = ActiveAlertManager()
    inactive = InactiveAlertManager()
    accepted = AcceptedAlertManager()
    completed = CompletedAlertManager()
    disarmed = DisarmedAlertManager()
    new = NewAlertManager()
    pending = PendingAlertManager()
    initiated_by_chat = InitiatedByChatAlertManager()
    initiated_by_emergency = InitiatedByEmergencyAlertManager()
    initiated_by_timer = InitiatedByTimerAlertManager()

    class Meta:
        ordering = ['-creation_date']

    def save(self, *args, **kwargs):
        super(Alert, self).save(*args, **kwargs)
        if self.status == 'C':
            if not self.completed_time:
                self.completed_time = datetime.now()
            try:
                profile = self.agency_user.get_profile()
                profile.delete()
            except UserProfile.DoesNotExist:
                pass
            self.store_chat_messages()
        elif self.status != 'N':
            if self.status == 'A':
                if not self.accepted_time:
                    self.accepted_time = datetime.now()
            elif self.status == 'P':
                if not self.pending_time:
                    self.pending_time = datetime.now()
            super(Alert, self).save(*args, **kwargs)
                
    def disarm(self):
        if not self.disarmed_time:
            self.disarmed_time = datetime.now()
            self.save()

    def store_chat_messages(self):
        from aws.dynamodb import DynamoDBManager
        db = DynamoDBManager()
        messages = db.get_messages_for_alert(self.pk)
        senders = {self.agency_user.pk: self.agency_user}
        if self.agency_dispatcher:
            senders[self.agency_dispatcher.pk] = self.agency_dispatcher
        sender_ids = [msg['sender_id'] for msg in messages]
        known_senders = senders.keys()
        unknown_senders = list(set(sender_ids) - set(known_senders))
        if unknown_senders:
            unknowns = AgencyUser.objects.filter(pk__in=unknown_senders)
            for unknown in unknowns:
                senders[unknown.pk] = unknown
        existing_messages = ChatMessage.objects.filter(alert=self)
        existing_message_ids = [msg.message_id for msg in existing_messages]
        for message in messages:
            if message['message_id'] in existing_message_ids:
                continue
            try:
                timestamp = float(message['timestamp'])
                timestamp = datetime.fromtimestamp(timestamp)
            except ValueError:
                timestamp = datetime.now()
            ChatMessage.objects.bulk_create(
                [
                    ChatMessage(alert=self,
                                sender=senders[message['sender_id']],
                                message=message['message'],
                                message_id=message['message_id'],
                                message_sent_time=timestamp)
                ]
            )


class AlertLocation(TimeStampedModel):
    alert = models.ForeignKey('Alert', related_name='locations')
    accuracy = models.FloatField(null=True, blank=True)
    altitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)    

    class Meta:
        ordering = ['-creation_date']

    def save(self, *args, **kwargs):
        super(AlertLocation, self).save(*args, **kwargs)
        self.alert.save()


class MassAlert(TimeStampedModel):
    agency = models.ForeignKey('Agency')
    agency_dispatcher = models.ForeignKey(settings.AUTH_USER_MODEL)
    message = models.TextField()

    class Meta:
        ordering = ['-creation_date']


class AgencyUser(AbstractUser):
    DEVICE_TYPE_CHOICES = (
        ('I', 'iOS'),
        ('A', 'Android'),
        ('B', 'Blackberry'),
        ('W', 'Windows'),
    )

    agency = models.ForeignKey('Agency', null=True, blank=True)
    phone_number = models.CharField(max_length=24)
    phone_number_verification_code = models.PositiveIntegerField()
    phone_number_verified = models.BooleanField(default=False)
    disarm_code = models.CharField(max_length=10)
    email_verified = models.BooleanField(default=False)
    device_token = models.CharField(max_length=255, null=True, blank=True)
    device_endpoint_arn = models.CharField(max_length=255,
                                           null=True, blank=True)
    device_type = models.CharField(max_length=2, null=True, blank=True,
                                   choices=DEVICE_TYPE_CHOICES)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username',]

    def save(self, *args, **kwargs):
        if not self.phone_number_verification_code:
            self.phone_number_verification_code =\
                random.randrange(10001, 700000)
        super(AgencyUser, self).save(*args, **kwargs)

    def sms_verification_topic_name(self):
        return u"sms-verification-topic-%s" % slugify(self.phone_number)

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
        ('SI', 'Sister'),
        ('FR', 'Friend'),
        ('O', 'Other'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, unique=True)
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
    profile_image = models.ImageField(upload_to='images/profiles',
                                      null=True, blank=True)
    profile_image_url = models.CharField(max_length=255, null=True, blank=True,
                                         help_text="Location of asset on S3")


class ChatMessage(TimeStampedModel):
    alert = models.ForeignKey('Alert')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL)
    message = models.TextField()
    message_id = models.CharField(max_length=100, unique=True)
    message_sent_time = models.DateTimeField(default=django.utils.timezone.now)

    class Meta:
        ordering = ['message_sent_time']

    def __unicode__(self):
        return u"%s - %s..." % (self.sender.first_name, self.message[:50])


@receiver(post_save, sender=AgencyUser)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(pre_save, sender=UserProfile)
def delete_profile_image_if_changed(sender, instance, **kwargs):
    try:
        obj = UserProfile.objects.get(pk=instance.pk)
    except UserProfile.DoesNotExist:
        pass
    else:
        if obj.profile_image_url and\
                not obj.profile_image_url == instance.profile_image_url:
            from core.tasks import delete_file_from_s3
            delete_file_from_s3.delay(obj.profile_image_url)


@receiver(post_delete, sender=UserProfile)
def delete_profile_image(sender, instance, **kwargs):
    if instance.profile_image_url:
        from core.tasks import delete_file_from_s3
        delete_file_from_s3.delay(instance.profile_image_url)


@receiver(pre_save, sender=AgencyUser)
def send_phone_number_verification_code(sender, instance, **kwargs):
    perform_check_anyway = False
    try:
        obj = AgencyUser.objects.get(pk=instance.pk)
    except AgencyUser.DoesNotExist:
        perform_check_anyway = True
    else:
        if not obj.phone_number == instance.phone_number\
                or perform_check_anyway:
            from core.tasks import send_phone_number_verification
            send_phone_number_verification.delay(\
                instance.phone_number,
                instance.phone_number_verification_code)


def set_email_verified(sender, user, request, **kwargs):
    user.email_verified = True
    user.save()
user_activated.connect(set_email_verified)
