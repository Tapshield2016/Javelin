from __future__ import unicode_literals

from django.db import models
from django.core import urlresolvers
from django.conf import settings
from django.contrib.gis.db import models as db_models

from utils import *

from core.aws.s3_filefield import S3EnabledImageField
from core.base_model import TimeStampedModel

DEFAULT_AUTORESPONDER_MESSAGE = "Due to high volume, we are currently experiencing delays. " \
                                "Call 911 if you require immediate assistance."


class Agency(TimeStampedModel):

    dispatchers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="agency_access",

    )

    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255, default="tapshield.com")
    agency_point_of_contact =\
        models.ForeignKey(settings.AUTH_USER_MODEL,
                          related_name='agency_point_of_contact',
                          null=True,
                          blank=True,
                          on_delete=models.SET_NULL,
                          help_text="This will be the person with full account access.  "
                                    "Edit all settings, change/add payment, add/remove dispatchers, etc.")
    dispatcher_phone_number = models.CharField(max_length=24, default="5555555555")
    dispatcher_secondary_phone_number = models.CharField(max_length=24, default="555",
                                                         null=True, blank=True,
                                                         help_text="Defaults to 911 within apps unless specified")
    dispatcher_schedule_start = models.TimeField(null=True, blank=True)
    dispatcher_schedule_end = models.TimeField(null=True, blank=True)
    agency_boundaries = models.TextField(null=True, blank=True, help_text="For multiple boundaries use Regions")
    agency_center_from_boundaries = models.BooleanField(default=True)
    agency_center_latitude = models.FloatField(default=0)
    agency_center_longitude = models.FloatField(default=0)
    agency_center_point = db_models.PointField(geography=True,
                                               null=True, blank=True)
    agency_radius = models.FloatField(default=0)
    default_map_zoom_level = models.PositiveIntegerField(default=15)
    alert_mode_name = models.CharField(max_length=24, default="Campus Police",
                                       help_text="This can be changed on the wishes of the organization to be "
                                                 "'Police', 'Alert', etc.")
    alert_received_message = models.CharField(max_length=255, default="The authorities have been notified.")
    alert_completed_message = models.TextField(null=True, blank=True,
                                               default="Thank you for using TapShield. "
                                                       "Your alert session was completed by dispatcher <first_name>.")
    sns_primary_topic_arn = models.CharField(max_length=255,
                                             null=True, blank=True)
    require_domain_emails = models.BooleanField(default=True)
    display_command_alert = models.BooleanField(default=True)
    loop_alert_sound = models.BooleanField(default=True)
    launch_call_to_dispatcher_on_alert = models.BooleanField(default=True,
                                                             help_text="When a mobile user begins an alert, "
                                                                       "immediately launch a VoIP call to the primary "
                                                                       "dispatcher number for the user's organization.")
    show_agency_name_in_app_navbar = models.BooleanField(default=True)
    enable_chat_autoresponder = models.BooleanField(default=False,
                                                    help_text="If enabled, please set the chat autoresponder message "
                                                              "below if you wish to respond with something that "
                                                              "differs from the default text.",
                                                    verbose_name="enable chat auto-responder")
    chat_autoresponder_message =\
        models.TextField(null=True, blank=True,
                         default=DEFAULT_AUTORESPONDER_MESSAGE,
                         verbose_name="chat auto-responder message")
    enable_user_location_requests = models.BooleanField(default=False,
                                                        help_text="If enabled, this allows for Shield "
                                                                  "Command dispatchers to request the latest location "
                                                                  "from users belonging to the organization. "
                                                                  "This is accomplished by sending a push "
                                                                  "notification to the organization's SNS topic "
                                                                  "to prompt devices to send a location update "
                                                                  "in the background. This does not disturb "
                                                                  "the users.")
    agency_logo = models.URLField(null=True, blank=True,
                                  help_text="Set the location of the standard agency logo.")
    agency_alternate_logo = models.URLField(null=True, blank=True,
                                            help_text="This could be an inverted version of the "
                                                      "standard logo or other differently "
                                                      "colorized/formatted version.")
    agency_small_logo = models.URLField(null=True, blank=True,
                                        help_text="This could be a truncated or minimized form of the "
                                                  "logo, e.g. 'UF' versus the larger logo version.")
    agency_theme = models.TextField(null=True, blank=True, default="{}",
                                    help_text="Use properly formatted JSON here to provide data as necessary.")
    agency_info_url = models.CharField(max_length=255, null=True, blank=True,
                                        help_text="This could be a web page with important info "
                                                  "pertaining to emergency situations")
    agency_rss_url = models.CharField(max_length=255, null=True, blank=True,
                                       help_text="RSS feed for mass alerts already populated by "
                                                 "the system in use")
    spot_crime_days_visible = models.PositiveIntegerField(default=1)
    theme = models.ForeignKey('Theme', related_name='agency_theme', null=True, blank=True,
                              help_text="UI elements related to agency")
    branding = models.ForeignKey('Theme', related_name="branding_theme", null=True, blank=True,
                                 help_text="Internal UI elements for OEM partners")

    #Is account ready to be searched
    hidden = models.BooleanField(default=True, help_text="Hide organization from query list. Apps will no be "
                                                         "able to add until visible")
    #Mark all premium items True
    full_version = models.BooleanField(default=True, help_text="When checked all services will be made available")
    no_alerts = models.BooleanField(default=False, help_text="Auto-checked when no alert types are "
                                                             "available for internal use")
    #premium items
    crime_reports_available = models.BooleanField(default=True)

    #standard items
    emergency_call_available = models.BooleanField(default=True)
    alert_available = models.BooleanField(default=True)
    chat_available = models.BooleanField(default=True)
    yank_available = models.BooleanField(default=True)
    entourage_available = models.BooleanField(default=True)
    static_device_available = models.BooleanField(default=True)
    mass_alert_available = models.BooleanField(default=True)

    objects = models.Manager()
    geo = db_models.GeoManager()

    class Meta:
        db_table = 'agency_agency'
        ordering = ['name',]
        verbose_name_plural = "Agencies"

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        from core.tasks import (
            create_agency_topic,
            notify_waiting_users_of_congestion
        )

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

        # Find centroid
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

    class Meta:
        db_table = 'agency_closeddate'


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
        db_table = 'agency_period'
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
                'admin:agency_dispatchcenter_change', args=(self.id,)
            )
            return u'<a href="%s" target="_blank">View Schedule</a>' % changeform_url
        return u''
    changeform_link.allow_tags = True
    changeform_link.short_description = 'Schedule'   # omit column header

    class Meta:
        db_table = 'agency_dispatchcenter'


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

    objects = models.Manager()
    geo = db_models.GeoManager()

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

    class Meta:
        db_table = 'agency_region'


def file_path(self, filename):
    url = "themes/%s/%s" % (self.name, filename)
    return url


class Theme(models.Model):

    name = models.CharField(max_length=255)

    primary_color = models.CharField(
        max_length=8,
        null=True,
        blank=True,
        help_text="Primary color of an organization's logo or color scheme"
    )
    secondary_color = models.CharField(
        max_length=8,
        null=True,
        blank=True,
        help_text="Secondary color of an organization's logo or color scheme"
    )
    alternate_color = models.CharField(
        max_length=8,
        null=True,
        blank=True,
        help_text="Alternate color, maybe something neutral such as white"
    )

    small_logo = S3EnabledImageField(
        upload_to=file_path,
        null=True,
        blank=True,
        help_text="Truncated or minimized form of the logo, "
                  "e.g. 'UF' versus the larger logo version for organization lists."
    )
    navbar_logo = S3EnabledImageField(
        upload_to=file_path,
        null=True,
        blank=True,
        help_text="For light background on home screen"
    )
    navbar_logo_alternate = S3EnabledImageField(
        upload_to=file_path,
        null=True,
        blank=True,
        help_text="For dark background on alert screen"
    )
    map_overlay_logo = S3EnabledImageField(
        upload_to=file_path,
        null=True,
        blank=True,
        help_text="Large logo for overlaying on map geofence"
    )
    shield_command_logo = S3EnabledImageField(
        upload_to=file_path,
        null=True,
        blank=True,
        max_height=50,
        help_text="Logo re-sized for Shield Command. 10% top and bottom padding recommended"
    )

    class Meta:
        db_table = 'agency_theme'

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