from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.core import urlresolvers
from django.contrib.gis.db import models as db_models
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D

from agency.models import Agency

from pygeocoder import Geocoder


def closest_agency(point):

    dwithin = 20
    qs = Agency.geo.select_related('agency_point_of_contact')\
        .filter(agency_center_point__dwithin=(point, D(mi=dwithin)))\
        .distance(point).order_by('distance')

    if qs:
        return qs[0]

    return None


class StaticDevice(models.Model):

    class Meta:
        db_table = 'core_static_device'

    uuid = models.SlugField(max_length=255, unique=True,
                            help_text="Unique identifier (e.g. serial number)")
    type = models.CharField(max_length=255, null=True, blank=True, default="Emergency Phone",
                            help_text="Model number or device type")
    description = models.CharField(max_length=255, null=True, blank=True,
                                   help_text="(Auto-set if left empty by lat & lon Google Maps geocoder) "
                                             "Human readable identifier denoting location "
                                             "(e.g. building, street, landmark, etc.)")
    agency = models.ForeignKey(Agency,
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

    objects = models.Manager()
    geo = db_models.GeoManager()

    def save(self, *args, **kwargs):
        if self.latitude and self.longitude:
            self.location_point = Point(self.longitude,
                                      self.latitude)
            if not self.agency:
                agency = closest_agency(self.location_point)
                if agency:
                    self.agency = agency
            if not self.description:
                results = Geocoder.reverse_geocode(lat=float(self.latitude), lng=float(self.longitude))
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
