from django.contrib import admin
from reversion.admin import VersionAdmin
from django.contrib.gis.admin import OSMGeoAdmin

from django.forms.models import BaseInlineFormSet
from django.utils.safestring import mark_safe
from django.core import urlresolvers
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist

from core.models import AgencyUser
from models import Region, DispatchCenter, Period, ClosedDate, Theme, Agency
from staticdevice.models import StaticDevice


class StaticDeviceInline(admin.StackedInline):

    model = StaticDevice
    extra = 0
    fields = ('uuid', 'type', 'description', 'changeform_link')
    readonly_fields = ('changeform_link',)


class AgencyDispatchersSet(BaseInlineFormSet):
    def get_queryset(self):
        if not hasattr(self, '_queryset'):
            try:
                group = Group.objects.get(name='Dispatchers')
                qs = super(AgencyDispatchersSet, self).get_queryset().filter(groups=group)
                self.queryset = qs
            except ObjectDoesNotExist:
                pass
        return self.queryset


class AgencyUserInline(admin.StackedInline):
    model = AgencyUser
    extra = 0
    formset = AgencyDispatchersSet
    verbose_name = "Dispatcher"
    verbose_name_plural = "Dispatchers"
    fields = ('first_name', 'last_name', 'username', 'groups')


def hide(self, request, queryset):
        queryset.update(hidden=True)
hide.short_description = "Make selected agencies hidden to users"


def show(self, request, queryset):
        queryset.update(hidden=False)
show.short_description = "Make selected agencies public"


class PeriodInline(admin.StackedInline):
    model = Period
    extra = 0


class ClosedDateInline(admin.StackedInline):
    model = ClosedDate
    extra = 0


class RegionInline(admin.StackedInline):
    model = Region
    extra = 0


class DispatchCenterAdmin(admin.ModelAdmin):
    inlines = [ClosedDateInline, PeriodInline]


class DispatchCenterInline(admin.StackedInline):
    model = DispatchCenter
    extra = 0
    fields = ('name', 'phone_number', 'changeform_link')
    readonly_fields = ('changeform_link',)


class AgencyAdmin(VersionAdmin, OSMGeoAdmin):
    fieldsets = (
        ('Publish', {
                'fields': (['hidden',]),
        }),
        ('Account Administrator', {
                'fields': (['agency_point_of_contact',])
        }),
        ('Required Fields', {
                'fields': (['name', 'domain',
                            'require_domain_emails',
                            'dispatcher_phone_number',
                            'dispatcher_secondary_phone_number',
                            'alert_mode_name',])
        }),
        ('Payment Level', {
                'fields': (['full_version', 'no_alerts',]),
        }),
        ('Available Services', {
                'fields': (['crime_reports_available', 'emergency_call_available', 'alert_available',
                            'chat_available', 'yank_available', 'entourage_available',
                            'static_device_available', 'mass_alert_available',]),
        }),
        ('Location and Boundaries', {
                'fields': (['agency_boundaries', 'agency_center_from_boundaries', 'agency_center_latitude',
                            'agency_center_longitude', 'agency_center_point', 'agency_radius',
                            'default_map_zoom_level']),
        }),
        ('General Settings', {
                'fields': (['dispatcher_schedule_start',
                            'dispatcher_schedule_end',
                            'alert_completed_message', 'sns_primary_topic_arn', 'display_command_alert',
                            'loop_alert_sound',
                            'launch_call_to_dispatcher_on_alert',
                            'show_agency_name_in_app_navbar',
                            'enable_chat_autoresponder',
                            'chat_autoresponder_message',
                            'enable_user_location_requests',
                            'spot_crime_days_visible',])
        }),
        ('Theme', {
                'fields': (['theme', 'theme_link', 'branding', 'branding_link', 'agency_logo', 'agency_alternate_logo',
                            'agency_small_logo', 'agency_theme']),
        }),
        ('Optional Info', {
                'fields': (['agency_info_url', 'agency_rss_url',]),
        }),
    )
    inlines = [
        RegionInline, DispatchCenterInline, AgencyUserInline, StaticDeviceInline,
    ]
    readonly_fields = ['theme_link', 'branding_link',]
    search_fields = ['name', 'agency_point_of_contact__username', 'domain',]
    list_display = ('__unicode__', 'full_version', 'domain',
                    'require_domain_emails', 'agency_point_of_contact', 'hidden',)
    actions = [hide, show]
    raw_id_fields = ("agency_point_of_contact", "theme", "branding",)

    def theme_link(self, obj):
        change_url = urlresolvers.reverse('admin:core_theme_change', args=(obj.theme.id,))
        return mark_safe('<a href="%s">Edit %s</a>' % (change_url, obj.theme.name))
    theme_link.short_description = 'Theme options'

    def branding_link(self, obj):
        change_url = urlresolvers.reverse('admin:core_theme_change', args=(obj.branding.id,))
        return mark_safe('<a href="%s">Edit %s</a>' % (change_url, obj.branding.name))
    branding_link.short_description = 'Theme options'


class ThemeAdmin(admin.ModelAdmin):
    ordering = ['name',]

admin.site.register(Agency, AgencyAdmin)
admin.site.register(DispatchCenter, DispatchCenterAdmin)
admin.site.register(Theme, ThemeAdmin)