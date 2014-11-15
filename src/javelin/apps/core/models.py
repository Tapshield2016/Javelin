import string
import random
import reversion
import re

from django.core import urlresolvers

from datetime import datetime
from math import sin, cos, sqrt, atan2, radians

import django.utils.timezone

from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.gis.db import models as db_models
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db import models
from django.db.models.signals import post_delete, pre_save, post_save
from django.dispatch import receiver
from django.utils.text import slugify

from urlparse import urlparse, urlunparse, urljoin

from registration.signals import user_activated
from rest_framework.authtoken.models import Token

from emailmgr.models import EmailAddress

from managers import (ActiveAlertManager, InactiveAlertManager,
                      AcceptedAlertManager, CompletedAlertManager,
                      DisarmedAlertManager, NewAlertManager,
                      PendingAlertManager, InitiatedByChatAlertManager,
                      InitiatedByEmergencyAlertManager,
                      InitiatedByTimerAlertManager,
                      WaitingForActionAlertManager,
                      ShouldReceiveAutoResponseAlertManager,
                      TrackingEntourageSessionManager)

from core.aws.s3_filefield import S3EnabledImageField, S3URLField

from pygeocoder import Geocoder


def kilometers_between_coordinates(point1, point2):

    R = 6371 # km

    lat1 = radians(point1.x)
    lon1 = radians(point1.y)
    lat2 = radians(point2.x)
    lon2 = radians(point2.y)

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    return distance


def radius_from_center(point, boundaries):

    point2 = Point(0, 0)
    max_distance = 0

    for string in boundaries:
        split = string.split(',')
        point2.x = float(split[1])
        point2.y = float(split[0])

        distance = kilometers_between_coordinates(point, point2)

        if distance > max_distance:
            max_distance = distance

    return max_distance*0.621371 #miles


def centroid_from_boundaries(boundaries):

    x_coordinates = []
    y_coordinates = []

    for x in boundaries:
        split = x.split(',')
        x_coordinates.append(float(split[0]))
        y_coordinates.append(float(split[1]))

    signed_area = 0.0
    centroid = Point(0, 0)

    for i in range(len(x_coordinates)):

        x0 = x_coordinates[i];
        y0 = y_coordinates[i];

        j = i+1
        if i == len(x_coordinates)-1:
            j = 0

        x1 = x_coordinates[j];
        y1 = y_coordinates[j];
        a = x0*y1 - x1*y0;
        signed_area += a;
        centroid.x += (x0 + x1)*a;
        centroid.y += (y0 + y1)*a;

    signed_area *= 0.5;
    centroid.x /= (6.0*signed_area);
    centroid.y /= (6.0*signed_area);

    return centroid;


class TimeStampedModel(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Location(TimeStampedModel):

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    class Meta:
        abstract = True


class Agency(TimeStampedModel):
    DEFAULT_AUTORESPONDER_MESSAGE = "Due to high volume, we are currently experiencing delays. Call 911 if you require immediate assistance."

    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255)
    agency_point_of_contact =\
        models.ForeignKey(settings.AUTH_USER_MODEL,
                          related_name='agency_point_of_contact',
                          null=True, blank=True, help_text="This will be the person with full account access. "
                                                           "Edit all settings, change/add payment, add/remove dispatchers, etc.")
    dispatcher_phone_number = models.CharField(max_length=24)
    dispatcher_secondary_phone_number = models.CharField(max_length=24,
                                                         null=True, blank=True,
                                                         help_text="Defaults to 911 within apps unless specified")
    dispatcher_schedule_start = models.TimeField(null=True, blank=True)
    dispatcher_schedule_end = models.TimeField(null=True, blank=True)
    agency_boundaries = models.TextField(null=True, blank=True, help_text="For multiple boundaries use Regions")
    agency_center_from_boundaries = models.BooleanField(default=False)
    agency_center_latitude = models.FloatField()
    agency_center_longitude = models.FloatField()
    agency_center_point = db_models.PointField(geography=True,
                                               null=True, blank=True)
    agency_radius = models.FloatField(default=0)
    default_map_zoom_level = models.PositiveIntegerField(default=15)
    alert_mode_name = models.CharField(max_length=24, default="Police",
                                       help_text="This can be changed on the wishes of the organization to be 'Police', 'Alert', etc.")
    alert_received_message = models.CharField(max_length=255, default="The authorities have been notified.")
    alert_completed_message = models.TextField(null=True, blank=True,
                                               default="Thank you for using TapShield. "
                                                       "Your alert session was completed by dispatcher <first_name>.")
    sns_primary_topic_arn = models.CharField(max_length=255,
                                             null=True, blank=True)
    require_domain_emails = models.BooleanField(default=False)
    display_command_alert = models.BooleanField(default=False)
    loop_alert_sound = models.BooleanField(default=False)
    launch_call_to_dispatcher_on_alert = models.BooleanField(default=True, help_text="When a mobile user begins an alert, immediately launch a VoIP call to the primary dispatcher number for the user's organization.")
    show_agency_name_in_app_navbar = models.BooleanField(default=False)
    enable_chat_autoresponder = models.BooleanField(default=False, help_text="If enabled, please set the chat autoresponder message below if you wish to respond with something that differs from the default text.", verbose_name="enable chat auto-responder")
    chat_autoresponder_message =\
        models.TextField(null=True, blank=True,
                         default=DEFAULT_AUTORESPONDER_MESSAGE,
                         verbose_name="chat auto-responder message")
    enable_user_location_requests = models.BooleanField(default=False, help_text="If enabled, this allows for Shield Command dispatchers to request the latest location from users belonging to the organization. This is accomplished by sending a push notification to the organization's SNS topic to prompt devices to send a location update in the background. This does not disturb the users.")
    agency_logo = models.URLField(null=True, blank=True,
                                  help_text="Set the location of the standard agency logo.")
    agency_alternate_logo = models.URLField(null=True, blank=True,
                                            help_text="This could be an inverted version of the standard logo or other differently colorized/formatted version.")
    agency_small_logo = models.URLField(null=True, blank=True,
                                        help_text="This could be a truncated or minimized form of the logo, e.g. 'UF' versus the larger logo version.")
    agency_theme = models.TextField(null=True, blank=True, default="{}",
                                    help_text="Use properly formatted JSON here to provide data as necessary.")
    agency_info_url = models.CharField(max_length=255, null=True, blank=True,
                                        help_text="This could be a web page with important info pertaining to emergency situations")
    agency_rss_url = models.CharField(max_length=255, null=True, blank=True,
                                       help_text="RSS feed for mass alerts already populated by the system in use")
    spot_crime_days_visible = models.PositiveIntegerField(default=1)
    theme = models.ForeignKey('Theme', related_name='agency_theme', null=True, blank=True,
                              help_text="UI elements related to agency")
    branding = models.ForeignKey('Theme', related_name="branding_theme", null=True, blank=True,
                                 help_text="UI elements for OEM partners")


    #Is account ready to be searched
    hidden = models.BooleanField(default=True, help_text="Hide organization from query list. Apps will no be "
                                                         "able to add until visible")

    #Mark all premium items True
    full_version = models.BooleanField(default=False, help_text="When checked all services will be made available")
    no_alerts = models.BooleanField(default=False, help_text="Auto-checked when no alert types are "
                                                             "available for internal use")

    #standard items
    crime_reports_available = models.BooleanField(default=True)

    #premium items
    emergency_call_available = models.BooleanField(default=False)
    alert_available = models.BooleanField(default=False)
    chat_available = models.BooleanField(default=False)
    yank_available = models.BooleanField(default=False)
    entourage_available = models.BooleanField(default=False)
    static_device_available = models.BooleanField(default=False)
    mass_alert_available = models.BooleanField(default=False)

    objects = models.Manager()
    geo = db_models.GeoManager()

    class Meta:
        ordering = ['name',]
        verbose_name_plural = "Agencies"

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        from tasks import (create_agency_topic,
                           notify_waiting_users_of_congestion)

        if not self.alert_completed_message:
            self.alert_completed_message = Agency._meta.get_field('alert_completed_message').get_default()

        if self.full_version:
            self.crime_reports_available = True
            self.emergency_call_available = True
            self.alert_available = True
            self.chat_available = True
            self.yank_available = True
            self.entourage_available = True
            self.static_device_available = True
            self.mass_alert_available = True

        if not self.emergency_call_available\
                and not self.alert_available\
                and not self.chat_available \
                and not self.yank_available \
                and not self.entourage_available\
                and not self.static_device_available:
            self.no_alerts = True
        else:
            self.no_alerts = False

        boundaries = None

        if self.agency_boundaries and self.agency_center_from_boundaries:
            boundaries = eval(self.agency_boundaries)

        #Find centroid
        if boundaries:

            centroid = centroid_from_boundaries(boundaries)
            self.agency_center_latitude = centroid.x
            self.agency_center_longitude = centroid.y

        if self.agency_center_latitude and self.agency_center_longitude:
            self.agency_center_point = Point(self.agency_center_longitude,
                                             self.agency_center_latitude)

        if self.agency_radius==0 and self.agency_boundaries:
            radius = radius_from_center(self.agency_center_point, eval(self.agency_boundaries))+.5
            self.agency_radius = round(radius,2)

        if not self.chat_autoresponder_message:
            self.chat_autoresponder_message =\
                Agency.DEFAULT_AUTORESPONDER_MESSAGE

        super(Agency, self).save(*args, **kwargs)
        if not self.sns_primary_topic_arn:
            create_agency_topic.delay(self.pk)
        if self.enable_chat_autoresponder:
            notify_waiting_users_of_congestion.delay(self.pk)


class ClosedDate(models.Model):

    dispatch_center = models.ForeignKey('DispatchCenter',
                                        related_name="closed_date")
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)


class Period(models.Model):

    DAY = (
        ('1', 'Sunday'),
        ('2', 'Monday'),
        ('3', 'Tuesday'),
        ('4', 'Wednesday'),
        ('5', 'Thursday'),
        ('6', 'Friday'),
        ('7', 'Saturday'),
    )

    dispatch_center = models.ForeignKey('DispatchCenter',
                                        related_name="opening_hours")
    day = models.CharField(max_length=1,
                           choices=DAY,
                           default='1')
    open = models.TimeField(null=True, blank=True)
    close = models.TimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Period"
        verbose_name_plural = "Opening Hours"
        ordering = ['day']


class DispatchCenter(models.Model):

    agency = models.ForeignKey('Agency',
                               related_name="dispatch_center")
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=24)

    def __unicode__(self):
        return u'%s - %s' % (self.agency.name, self.name)

    def changeform_link(self):
        if self.id:
            changeform_url = urlresolvers.reverse(
                'admin:core_dispatchcenter_change', args=(self.id,)
            )
            return u'<a href="%s" target="_blank">View Schedule</a>' % changeform_url
        return u''
    changeform_link.allow_tags = True
    changeform_link.short_description = 'Schedule'   # omit column header


class Region(models.Model):

    agency = models.ForeignKey('Agency',
                               related_name="region")
    name = models.CharField(max_length=255)
    primary_dispatch_center = models.ForeignKey('DispatchCenter',
                                                related_name='primary_dispatch_center')
    secondary_dispatch_center = models.ForeignKey('DispatchCenter',
                                                  related_name='secondary_dispatch_center',
                                                  null=True, blank=True)
    fallback_dispatch_center = models.ForeignKey('DispatchCenter',
                                                 related_name='fallback_dispatch_center',
                                                 null=True, blank=True)
    boundaries = models.TextField(null=True, blank=True)
    center_latitude = models.FloatField()
    center_longitude = models.FloatField()
    center_point = db_models.PointField(geography=True,
                                        null=True, blank=True)
    radius = models.FloatField(default=0)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):

        boundaries = None

        if self.boundaries:
            boundaries = eval(self.boundaries)

        #Find centroid
        if boundaries:

            centroid = centroid_from_boundaries(boundaries)
            self.center_latitude = centroid.x
            self.center_longitude = centroid.y

        if self.center_latitude and self.center_longitude:
            self.center_point = Point(self.center_longitude,
                                      self.center_latitude)

        if self.radius==0 and self.boundaries:
            radius = radius_from_center(self.center_point, eval(self.boundaries))+.5
            self.radius = round(radius,2)

        super(Region, self).save(*args, **kwargs)


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

    agency = models.ForeignKey('Agency')
    agency_user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    related_name="alert_agency_user",
                                    blank=True, null=True)
    static_device = models.ForeignKey('StaticDevice',
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
    user_notified_of_receipt = models.BooleanField(default=False, help_text="Indicates if a push notification has been sent to the user to notify the app that the alert has been received.")
    user_notified_of_dispatcher_congestion = models.BooleanField(default=False, help_text="If an organization has the chat auto-responder functionality enabled, this flag is to indicate if the user has been sent the auto-responder message.")
    notes = models.TextField(null=True, blank=True)

    call_length = models.PositiveSmallIntegerField(null=True, blank=True)

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
    initiated_by_chat = InitiatedByChatAlertManager()
    initiated_by_emergency = InitiatedByEmergencyAlertManager()
    initiated_by_timer = InitiatedByTimerAlertManager()

    class Meta:
        ordering = ['-creation_date']

    def __unicode__(self):
        string = None
        if self.static_device:
            string = u"%s" % self.static_device.uuid
        if self.agency_user:
            string = u"%s" % self.agency_user.email
        return string

    @reversion.create_revision()
    def save(self, *args, **kwargs):
        super(Alert, self).save(*args, **kwargs)
        if self.status == 'C':
            if not self.completed_time:
                self.completed_time = datetime.now()

            if self.agency_user:
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
    agency = models.ForeignKey('Agency')
    agency_dispatcher = models.ForeignKey(settings.AUTH_USER_MODEL)
    message = models.TextField()
    type = models.CharField(max_length=2, null=True, blank=True,
                                   choices=MASS_ALERT_TYPE)

    class Meta:
        ordering = ['-creation_date']

    def __unicode__(self):
        return u"%s" % self.message


class AgencyUser(AbstractUser):

    DEVICE_TYPE_CHOICES = (
        ('I', 'iOS'),
        ('A', 'Android'),
        ('B', 'Blackberry'),
        ('W', 'Windows'),
    )

    agency = models.ForeignKey('Agency', null=True, blank=True)
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
    last_reported_latitude = models.FloatField(null=True, blank=True)
    last_reported_longitude = models.FloatField(null=True, blank=True)
    last_reported_point = db_models.PointField(geography=True,
                                               null=True, blank=True)
    last_reported_time = models.DateTimeField(null=True, blank=True)
    notify_entourage_on_alert = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username',]

    objects = UserManager()
    geo = db_models.GeoManager()

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
        if self.last_reported_latitude and self.last_reported_longitude:
            self.last_reported_point = Point(self.last_reported_longitude,
                                             self.last_reported_latitude)

        if not self.email:
            self.email = self.username+"@noemail.com"

        if self.phone_number:
            self.phone_number = re.sub("\D", "", self.phone_number)

        super(AgencyUser, self).save(*args, **kwargs)

    def sms_verification_topic_name(self):
        return u"sms-verification-topic-%s" % slugify(self.phone_number)

AgencyUser._meta.get_field_by_name('email')[0]._unique=True


class EntourageSession(TimeStampedModel):

    TRACKING_STATUS_CHOICES = (
        ('T', 'Tracking'),
        ('A', 'Arrived'),
        ('N', 'Non-Arrival'),
        ('C', 'Cancelled'),
        ('U', 'Unknown'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='session_user')
    status = models.CharField(max_length=1, choices=TRACKING_STATUS_CHOICES,
                              default='T')
    start_location = models.ForeignKey('NamedLocation', null=True, blank=True, related_name="starting_locations")
    end_location = models.ForeignKey('NamedLocation', null=True, blank=True, related_name="ending_locations")
    eta = models.DateTimeField(null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    arrival_time = models.DateTimeField(null=True, blank=True)
    entourage_notified = models.BooleanField(default=False)

    # Managers
    objects = models.Manager()
    tracking = TrackingEntourageSessionManager()

    class Meta:
        ordering = ['-creation_date']

    def __unicode__(self):
        return u"%s - %s to %s" % (self.user.username, self.start_location.name, self.end_location.name)


class NamedLocation(Location):

    name = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)

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
                                     null=True, blank=True)

    always_visible = models.BooleanField(default=False)
    track_route = models.BooleanField(default=True)
    notify_arrival = models.BooleanField(default=True)
    notify_non_arrival = models.BooleanField(default=True)
    notify_yank = models.BooleanField(default=True)
    notify_called_911 = models.BooleanField(default=False)

    def save(self, *args, **kwargs):

        if self.email_address:
            self.email_address = self.email_address.lower()

        if self.phone_number:
            self.phone_number = re.sub("\D", "", self.phone_number)

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
    profile_image_url = S3URLField(null=True, blank=True,
                                   help_text="Location of asset on S3")

    def __unicode__(self):
        return self.user.username


class ChatMessage(TimeStampedModel):
    alert = models.ForeignKey('Alert')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL)
    message = models.TextField()
    message_id = models.CharField(max_length=100, unique=True)
    message_sent_time = models.DateTimeField(default=django.utils.timezone.now)

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

    reporter = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 related_name="reporter")
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
                                              blank=True, null=True)
    viewed_time = models.DateTimeField(null=True, blank=True)
    viewed_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  related_name="viewed_by",
                                  blank=True, null=True)
                                        

    objects = db_models.GeoManager()

    def save(self, *args, **kwargs):
        if self.report_latitude and self.report_longitude:
            self.report_point = Point(self.report_longitude,
                                      self.report_latitude)
        super(SocialCrimeReport, self).save(*args, **kwargs)


class StaticDevice(models.Model):

    uuid = models.SlugField(max_length=255, unique=True,
                            help_text="Unique identifier (e.g. serial number)")
    type = models.CharField(max_length=255, null=True, blank=True, default="Emergency Phone",
                            help_text="Model number or device type")
    description = models.CharField(max_length=255, null=True, blank=True,
                                   help_text="(Auto-set if left empty by lat & lon Google Maps geocoder) "
                                             "Human readable identifier denoting location "
                                             "(e.g. building, street, landmark, etc.)")
    agency = models.ForeignKey('Agency',
                               related_name="StaticDevice",
                               null=True, blank=True,
                               help_text="(Auto-set if left empty by lat & lon to nearest within 10 miles) Who should receive the alert?")
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location_point = db_models.PointField(geography=True,
                                          null=True, blank=True,
                                          help_text="(Auto-set by lat & lon) Coordinate point used by geoDjango for querying"
                                                    "Note: The lat & lon is reversed to conform to a coordinate plane")
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                              related_name="User",
                              null=True, blank=True,
                              help_text="Will be used in the future to limit edit/updated permissions "
                                        "to a particular authorization token")

    def save(self, *args, **kwargs):
        if self.latitude and self.longitude:
            self.location_point = Point(self.longitude,
                                      self.latitude)
            if not self.agency:
                agency = closest_agency(self.location_point)
                if agency:
                    self.agency = agency
            if not self.description:
                results = Geocoder.reverse_geocode(self.latitude, self.longitude)
                top_result = results[0]
                if top_result:
                    self.description = top_result.route
        if not self.type:
            self.type = "Emergency Phone"

        super(StaticDevice, self).save(*args, **kwargs)

    def __unicode__(self):
        if self.agency and self.uuid:
            return u'%s - %s' % (self.agency.name, self.uuid)
        elif self.uuid:
            return u'%s' % self.uuid

        return u'%s' % self.id

    def changeform_link(self):
        if self.id:
            changeform_url = urlresolvers.reverse(
                'admin:core_staticdevice_change', args=(self.id,)
            )
            return u'<a href="%s" target="_blank">View more options</a>' % changeform_url
        return u''
    changeform_link.allow_tags = True
    changeform_link.short_description = 'Options'   # omit column header


def file_path(self, filename):
    url = "themes/%s/%s" % (self.name, filename)
    return url


class Theme(models.Model):

    name = models.CharField(max_length=255)

    primary_color = models.CharField(max_length=8, null=True, blank=True,
                                     help_text="Primary color of an organization's logo or color scheme")
    secondary_color = models.CharField(max_length=8, null=True, blank=True,
                                       help_text="Secondary color of an organization's logo or color scheme")
    alternate_color = models.CharField(max_length=8, null=True, blank=True,
                                       help_text="Alternate color, maybe something neutral such as white")

    small_logo = S3EnabledImageField(upload_to=file_path, null=True, blank=True,
                                     help_text="Truncated or minimized form of the logo, e.g. 'UF' versus the larger logo version for organization lists.")
    navbar_logo = S3EnabledImageField(upload_to=file_path, null=True, blank=True,
                                     help_text="For light background on home screen")
    navbar_logo_alternate = S3EnabledImageField(upload_to=file_path, null=True, blank=True,
                                     help_text="For dark background on alert screen")
    map_overlay_logo = S3EnabledImageField(upload_to=file_path, null=True, blank=True,
                                     help_text="Large logo for overlaying on map geofence")
    shield_command_logo = S3EnabledImageField(upload_to=file_path, null=True, blank=True, max_height=50,
                                              help_text="Logo re-sized for Shield Command. 10% top and bottom padding recommended")

    def __unicode__(self):
        return u'%s' % self.name

    def small_logo_s3_url(self):
        return self.small_logo.secure_s3_url() if self.small_logo else None

    def navbar_logo_s3_url(self):
        return self.navbar_logo.secure_s3_url() if self.navbar_logo else None

    def navbar_logo_alternate_s3_url(self):
        return self.navbar_logo_alternate.secure_s3_url() if self.navbar_logo_alternate else None

    def map_overlay_logo_s3_url(self):
        return self.map_overlay_logo.secure_s3_url() if self.map_overlay_logo else None


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


def closest_agency(point):

    dwithin = 20
    qs = Agency.geo.select_related('agency_point_of_contact')\
                .filter(agency_center_point__dwithin=(point,
                                                      D(mi=dwithin)))\
                .distance(point).order_by('distance')

    if qs:
        return qs[0]

    return None
