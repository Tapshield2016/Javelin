import string
import random
from reversion import revisions as reversion
import re

from django.core import validators
from django.core.mail import send_mail

from datetime import datetime, timedelta

from django.utils import timezone

from django.conf import settings
from django.contrib.auth.models import UserManager, AbstractBaseUser, PermissionsMixin
from django.contrib.gis.db import models as db_models
from django.contrib.gis.geos import Point
from django.db import models, transaction
from django.db.models.signals import post_delete, pre_save, post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from base_model import TimeStampedModel, Location

from registration.signals import user_activated
from rest_framework.authtoken.models import Token

from emailmgr.models import EmailAddress

from staticdevice.models import StaticDevice

from agency.models import Agency

from managers import (
    ActiveAlertManager,
    InactiveAlertManager,
    AcceptedAlertManager,
    CompletedAlertManager,
    DisarmedAlertManager,
    NewAlertManager,
    PendingAlertManager,
    InitiatedByChatAlertManager,
    InitiatedByEmergencyAlertManager,
    InitiatedByTimerAlertManager,
    InitiatedByCallAlertManager,
    InitiatedByYankAlertManager,
    WaitingForActionAlertManager,
    ShouldReceiveAutoResponseAlertManager,
    TrackingEntourageSessionManager
)

from aws.s3_filefield import S3URLField


class Alert(TimeStampedModel):
    STATUS_CHOICES = (
        ('A', 'Accepted'),
        ('C', 'Completed'),
        ('N', 'New'),
        ('P', 'Pending'),
        ('U', 'Unavailable'),
    )

    ALERT_INITIATED_BY_CHOICES = (
        ('N', '911'), #Red
        ('E', 'Call'), #Orange
        ('T', 'Timer'), #Yellow
        ('Y', 'Yank'), #Yellow
        ('C', 'Chat'), #Green
        ('S', 'Static'), #Blue
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

    agency = models.ForeignKey(Agency)
    agency_user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    related_name="alert_agency_user",
                                    blank=True, null=True)
    static_device = models.ForeignKey(StaticDevice,
                                      related_name="static_device",
                                      blank=True, null=True)
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
    user_notified_of_receipt = models.BooleanField(default=False,
                                                   help_text="Indicates if a push notification has "
                                                             "been sent to the user to notify the app "
                                                             "that the alert has been received.")
    user_notified_of_dispatcher_congestion = models.BooleanField(default=False,
                                                                 help_text="If an organization has the "
                                                                           "chat auto-responder functionality "
                                                                           "enabled, this flag is to indicate if "
                                                                           "the user has been sent the "
                                                                           "auto-responder message.")
    notes = models.TextField(null=True, blank=True)

    call_length = models.PositiveSmallIntegerField(null=True, blank=True)
    in_bounds = models.BooleanField(default=True)

    notified_entourage = models.BooleanField(default=False)

    objects = models.Manager()
    active = ActiveAlertManager()
    inactive = InactiveAlertManager()
    waiting_for_action = WaitingForActionAlertManager()
    should_receive_autoresponse = ShouldReceiveAutoResponseAlertManager()
    accepted = AcceptedAlertManager()
    completed = CompletedAlertManager()
    disarmed = DisarmedAlertManager()
    new = NewAlertManager()
    pending = PendingAlertManager()

    initiated_by_emergency = InitiatedByEmergencyAlertManager()
    initiated_by_yank = InitiatedByYankAlertManager()
    initiated_by_chat = InitiatedByChatAlertManager()
    initiated_by_call = InitiatedByCallAlertManager()
    initiated_by_timer = InitiatedByTimerAlertManager()

    class Meta:
        ordering = ['-creation_date']

    def __unicode__(self):
        name = None
        if self.static_device:
            name = u"%s" % self.static_device.uuid
        if self.agency_user:
            name = u"%s" % self.agency_user.username
        return name

    # @transaction.atomic()
    # @reversion.create_revision()
    def save(self, *args, **kwargs):
        from notifications import send_called_emergency_notifications, send_yank_alert_notifications
        super(Alert, self).save(*args, **kwargs)
        if self.status == 'C':
            if not self.completed_time:
                self.completed_time = datetime.now()

            if self.agency_user:
                try:
                    profile = self.agency_user.profile
                    profile.save()
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

        if not self.notified_entourage and self.status != 'C':
            self.notified_entourage = True
            active_sessions = EntourageSession.tracking.filter(user=self.agency_user)
            if active_sessions:
                session = active_sessions[0]
                if self.initiated_by == 'T':
                    session.non_arrival()

            if self.initiated_by == 'N':
                send_called_emergency_notifications(self.agency_user, self)

            if self.initiated_by == 'Y':
                send_yank_alert_notifications(self.agency_user, self)

        super(Alert, self).save(*args, **kwargs)

    def disarm(self):
        if not self.disarmed_time:
            self.disarmed_time = datetime.now()
            self.save()

    def store_chat_messages(self):
        from aws.dynamodb import DynamoDBManager

        if not self.agency_user:
            return

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
                sender_id = int(message['sender_id'])
            except ValueError:
                timestamp = datetime.now()
            ChatMessage.objects.bulk_create(
                [
                    ChatMessage(alert=self,
                                sender=senders[sender_id],
                                message=message['message'],
                                message_id=message['message_id'],
                                message_sent_time=timestamp)
                ]
            )


class AlertLocation(TimeStampedModel):

    alert = models.ForeignKey('Alert', related_name='locations')
    accuracy = models.FloatField(null=True, blank=True)
    altitude = models.FloatField(null=True, blank=True)
    floor_level = models.IntegerField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['-creation_date']

    def save(self, *args, **kwargs):
        super(AlertLocation, self).save(*args, **kwargs)
        self.alert.save()


class MassAlert(Location):

    MASS_ALERT_TYPE = (
        ('AB', 'Abuse'),
        ('AR', 'Arrest'),
        ('AN', 'Arson'),
        ('AS', 'Assault'),
        # ('BL', 'Bleeding'),
        # ('BB', 'Broken Bone'),
        ('BU', 'Burglary'),
        ('CA', 'Car Accident'),
        # ('CH', 'Choking'),
        # ('CP', 'CPR'),
        ('DI', 'Disturbance'),
        ('DR', 'Drugs/Alcohol'),
        ('H', 'Harassment'),
        # ('HA', 'Heart Attack'),
        # ('HF', 'High Fever'),
        ('MH', 'Mental Health'),
        ('O', 'Other'),
        ('R', 'Robbery'),
        ('SH', 'Shooting'),
        # ('ST', 'Stroke'),
        ('S', 'Suggestion'),
        ('SA', 'Suspicious Activity'),
        ('T', 'Theft'),
        ('V', 'Vandalism'),
    )

    address = models.CharField(max_length=255, null=True, blank=True)
    agency = models.ForeignKey(Agency)
    agency_dispatcher = models.ForeignKey(settings.AUTH_USER_MODEL)
    message = models.TextField()
    type = models.CharField(max_length=2, null=True, blank=True,
                                   choices=MASS_ALERT_TYPE)

    class Meta:
        ordering = ['-creation_date']

    def __unicode__(self):
        return u"%s" % self.message


class AgencyUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        'username',
        max_length=255,
        unique=True,
        help_text='Required. 255 characters or fewer. Letters, digits and @/./+/-/_ only.',
        validators=[
            validators.RegexValidator(
                r'^[\w.@+-]+$',
                'Enter a valid username. This value may contain only '
                'letters, numbers ' 'and @/./+/-/_ characters.'
            ),
        ],
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )
    first_name = models.CharField('first name', max_length=30, blank=True)
    last_name = models.CharField('last name', max_length=30, blank=True)
    email = models.EmailField('email address', blank=True, unique=True)
    is_staff = models.BooleanField(
        'staff status',
        default=False,
        help_text='Designates whether the user can log into this admin site.',
    )
    is_active = models.BooleanField(
        'active',
        default=True,
        help_text='Designates whether this user should be treated as active. '
                  'Unselect this instead of deleting accounts.',
    )
    date_joined = models.DateTimeField('date joined', default=timezone.now)

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', ]

    objects = UserManager()
    geo = db_models.GeoManager()

    DEVICE_TYPE_CHOICES = (
        ('I', 'iOS'),
        ('A', 'Android'),
        ('B', 'Blackberry'),
        ('W', 'Windows'),
    )

    agency = models.ForeignKey(Agency, null=True, blank=True)
    phone_number = models.CharField(max_length=24, null=True, blank=True)
    phone_number_verification_code = models.PositiveIntegerField()
    phone_number_verified = models.BooleanField(default=False)
    disarm_code = models.CharField(max_length=10, null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    device_token = models.CharField(max_length=255, null=True, blank=True)
    device_endpoint_arn = models.CharField(max_length=255,
                                           null=True, blank=True)
    device_type = models.CharField(max_length=2, null=True, blank=True,
                                   choices=DEVICE_TYPE_CHOICES)
    user_declined_push_notifications = models.BooleanField(default=False)
    user_logged_in_via_social = models.BooleanField(default=False)
    notify_entourage_on_alert = models.BooleanField(default=False)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location_point = db_models.PointField(geography=True,
                                          null=True,
                                          blank=True)
    accuracy = models.FloatField(null=True, blank=True)
    altitude = models.FloatField(null=True, blank=True)
    floor_level = models.IntegerField(null=True, blank=True)
    location_timestamp = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        if self.email:
            return u"%s" % self.email
        elif self.username:
            return u"%s" % self.username

    def get_absolute_url(self):
        return "/api/v1/users/%i/" % self.id

    def save(self, *args, **kwargs):
        if not self.has_usable_password():
            self.set_password(''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(8)]));
        if not self.phone_number_verification_code:
            self.phone_number_verification_code =\
                random.randrange(1001, 9999)
        if self.latitude and self.longitude:
            self.location_point = Point(self.longitude,
                                        self.latitude)

        if not self.email:
            self.email = self.username+"@noemail.com"

        if self.phone_number:
            self.phone_number = re.sub("\D", "", self.phone_number)

        super(AgencyUser, self).save(*args, **kwargs)

    def sms_verification_topic_name(self):
        return u"sms-verification-topic-%s" % slugify(self.phone_number)

    def match_with_entourage_members(self):

        if self.phone_number_verified and self.phone_number:
            entourage_members_matching = EntourageMember.objects.filter(phone_number=self.phone_number)

            for member in entourage_members_matching:
                if member.user == self:
                    member.delete()
                else:
                    member.matched_user = self
                    member.save()


class EntourageSession(TimeStampedModel):

    TRACKING_STATUS_CHOICES = (
        ('T', 'Tracking'),
        ('A', 'Arrived'),
        ('N', 'Non-Arrival'),
        ('C', 'Cancelled'),
        ('U', 'Unknown'),
    )

    TRAVEL_MODES = (
        ('D', 'Driving'),
        ('W', 'Walking'),
        ('B', 'Bicycling'),
        ('T', 'Transit'),
        ('U', 'Unknown'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='session_user'
    )
    status = models.CharField(
        max_length=1,
        choices=TRACKING_STATUS_CHOICES,
        default='T'
    )
    travel_mode = models.CharField(
        max_length=1,
        choices=TRAVEL_MODES,
        default='U'
    )
    start_location = models.ForeignKey(
        'NamedLocation',
        null=True,
        blank=True,
        related_name="starting_locations"
    )
    end_location = models.ForeignKey(
        'NamedLocation',
        null=True,
        blank=True,
        related_name="ending_locations"
    )
    eta = models.DateTimeField(null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    arrival_time = models.DateTimeField(null=True, blank=True)
    entourage_notified = models.BooleanField(default=False)

    # Managers
    objects = models.Manager()
    tracking = TrackingEntourageSessionManager()

    class Meta:
        ordering = ['-creation_date']

    def save(self, *args, **kwargs):
        if self.status == "T":
            five_after = self.eta + timedelta(minutes=10)
            if five_after < datetime.utcnow().replace(tzinfo=timezone.utc):
                self.status = "U"

        super(EntourageSession, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"%s - %s to %s" % (self.user.username, self.start_location.name, self.end_location.name)

    def arrived(self):
        from notifications import send_arrival_notifications

        message = None
        if not self.entourage_notified:
            self.entourage_notified = True
            message = send_arrival_notifications(self)

        self.arrival_time = datetime.now()
        self.status = "A"
        self.save()
        return message

    def non_arrival(self):
        from notifications import send_non_arrival_notifications

        message = None
        if not self.entourage_notified:
            self.entourage_notified = True
            message = send_non_arrival_notifications(self)

        self.status = "N"
        self.save()
        return message

    def cancel(self):
        self.status = "C"
        self.save()


class NamedLocation(Location):

    name = models.CharField(max_length=255, null=True, blank=True)
    formatted_address = models.CharField(max_length=255, null=True, blank=True)
    street = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    zip = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ['-creation_date']

    def __unicode__(self):
        return self.name


class TrackingLocation(Location):

    entourage_session = models.ForeignKey('EntourageSession', related_name='locations')
    accuracy = models.FloatField(null=True, blank=True)
    altitude = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['creation_date']

    def save(self, *args, **kwargs):
        super(TrackingLocation, self).save(*args, **kwargs)
        self.entourage_session.save()


class EntourageMember(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='entourage_members')
    name = models.CharField(max_length=255, null=True, blank=True)
    first = models.CharField(max_length=255, null=True, blank=True)
    last = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=24, null=True, blank=True)
    email_address = models.EmailField(max_length=254, null=True, blank=True)

    record_id = models.PositiveIntegerField(blank=True, null=True)

    matched_user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                     related_name='existing_user',
                                     null=True, blank=True, on_delete=models.SET_NULL)

    always_visible = models.BooleanField(default=False)
    track_route = models.BooleanField(default=True)
    notify_arrival = models.BooleanField(default=True)
    notify_non_arrival = models.BooleanField(default=True)
    notify_yank = models.BooleanField(default=True)
    notify_called_911 = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        from tasks import notify_user_added_to_entourage
        from notifications import added_by_user_message

        if self.email_address:
            self.email_address = self.email_address.lower()

        if self.phone_number:
            self.phone_number = re.sub("\D", "", self.phone_number)

        should_send_sns = False

        if not self.matched_user:
            should_send_sns = True

        if not self.matched_user and self.phone_number:

            users_matching_phone_number = AgencyUser.objects.filter(phone_number=self.phone_number)

            if users_matching_phone_number:
                for user in users_matching_phone_number:
                    if user.phone_number_verified:
                        self.matched_user = user

        if not self.matched_user and self.email_address:

            matching_email_address_objects = EmailAddress.objects.filter(email=self.email_address)

            if matching_email_address_objects:
                for email_object in matching_email_address_objects:
                    if email_object.is_active and email_object.is_primary:
                        self.matched_user = email_object.user
                    elif email_object.is_active and not self.matched_user:
                        self.matched_user = email_object.user

            if not self.matched_user:
                users_matching_email = AgencyUser.objects.filter(email=self.email_address)

                if users_matching_email:
                    for user in users_matching_email:
                        if user.email_verified:
                            self.matched_user = user

        if self.matched_user and should_send_sns:

            notify_user_added_to_entourage.delay(added_by_user_message(self.user),
                                                 self.user.id,
                                                 self.matched_user.device_type,
                                                 self.matched_user.device_endpoint_arn)

        super(EntourageMember, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"%s - %s" % (self.user.username, self.name)


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
        ('O', 'Other'),
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
        ('O', 'Other'),
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

    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="profile")
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
    profile_image_url = S3URLField(null=True, blank=True,
                                   help_text="Location of asset on S3")

    def __unicode__(self):
        return self.user.username


class ChatMessage(TimeStampedModel):
    alert = models.ForeignKey('Alert')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL)
    message = models.TextField()
    message_id = models.CharField(max_length=100, unique=True)
    message_sent_time = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['message_sent_time']

    def __unicode__(self):

        if self.message.__len__() < 47:
            return self.message

        return self.message[:50] + "..."


class SocialCrimeReport(TimeStampedModel):

    CRIME_TYPE_CHOICES = (
        ('AB', 'Abuse'),
        ('AS', 'Assault'),
        ('CA', 'Car Accident'),
        ('DI', 'Disturbance'),
        ('DR', 'Drugs/Alcohol'),
        ('H', 'Harassment'),
        ('MH', 'Mental Health'),
        ('O', 'Other'),
        ('RN', 'Repair Needed'),
        ('S', 'Suggestion'),
        ('SA', 'Suspicious Activity'),
        ('T', 'Theft'),
        ('V', 'Vandalism'),
    )

    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="reporter",
                                 blank=True, null=True, on_delete=models.SET_NULL)
    body = models.TextField()
    report_type = models.CharField(max_length=2, choices=CRIME_TYPE_CHOICES)
    report_audio_url = S3URLField(null=True, blank=True,
                                         help_text="Location of asset on S3")
    report_image_url = S3URLField(null=True, blank=True,
                                         help_text="Location of asset on S3")
    report_video_url = S3URLField(null=True, blank=True,
                                         help_text="Location of asset on S3")
    report_latitude = models.FloatField()
    report_longitude = models.FloatField()
    report_point = db_models.PointField(geography=True,
                                        null=True, blank=True)
    report_anonymous = models.BooleanField(default=False)
    flagged_spam = models.BooleanField(default=False)
    flagged_by_dispatcher = models.ForeignKey(settings.AUTH_USER_MODEL,
                                              related_name="flagged_by_dispatcher",
                                              blank=True, null=True, on_delete=models.SET_NULL)
    viewed_time = models.DateTimeField(null=True, blank=True)
    viewed_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  related_name="viewed_by",
                                  blank=True, null=True, on_delete=models.SET_NULL)

    objects = models.Manager()
    geo = db_models.GeoManager()

    def save(self, *args, **kwargs):
        if self.report_latitude and self.report_longitude:
            self.report_point = Point(self.report_longitude,
                                      self.report_latitude)
        super(SocialCrimeReport, self).save(*args, **kwargs)


class UserNotification(TimeStampedModel):

    NOTIFICATION_TYPES = (
        ('E', 'Entourage'),
        ('C', 'Crime Report'),
        ('O', 'Other'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name="notifications")
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=1, default='O', choices=NOTIFICATION_TYPES)
    read = models.BooleanField(default=False)

    limit = models.Q(app_label='core')
    content_type = models.ForeignKey(ContentType, null=True, limit_choices_to=limit)
    object_id = models.PositiveIntegerField(null=True)
    action_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['-creation_date']

    def __unicode__(self):
        if self.message.__len__() < 47:
            return self.user.username + " - " + self.message

        return self.user.username + " - " + self.message[:50] + "..."



@receiver(post_save, sender=EntourageMember)
def check_matched_user(sender, instance=None, created=False, **kwargs):
    if instance.matched_user:
        matched_users_with_user = EntourageMember.objects.filter(user=instance.user, matched_user=instance.matched_user).exclude(pk=instance.pk)
        for member in matched_users_with_user:
            member.delete()


@receiver(post_save, sender=EntourageSession)
def create_first_location(sender, instance=None, created=False, **kwargs):
    if created:
        locations = TrackingLocation.objects.filter(entourage_session=instance)
        if not locations:
            TrackingLocation.objects.create(latitude=instance.start_location.latitude,
                                            longitude=instance.start_location.longitude,
                                            entourage_session=instance)

@receiver(post_save, sender=AgencyUser)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

@receiver(post_save, sender=AgencyUser)
def create_primary_email_for_new_user(sender, instance, created, **kwargs):
    """
    Create a matching email address separate from that of User object when a user object is created.
    """
    # user was just created, so no worries about duplicate emails as it has been done before
    if instance.email:
        try:
            EmailAddress.objects.get(user=instance, email__iexact=instance.email.lower())
        except EmailAddress.DoesNotExist:
            e = EmailAddress(**{'user': instance,
                                'email': instance.email.lower(),
                                'is_primary': True,
                                'is_active': instance.email_verified})
            e.save()
            return

        if instance.email_verified:
            email = EmailAddress.objects.get(user=instance, email__iexact=instance.email.lower())
            if email:
                email.is_active = True
                email.save()

@receiver(post_delete, sender=AgencyUser)
def remove_all_emails_for_deleted_user(sender, instance, **kwargs):
    """
    Delete all emails addresses associated with this user that was just delete.
    """
    # user was just delete, delete any email associated with this user
    emails = EmailAddress.objects.filter(user=instance)
    for e in emails:
        e.delete()

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
    return
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