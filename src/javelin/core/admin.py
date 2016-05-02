from reversion import admin as reversion_admin

from django.forms.models import BaseInlineFormSet
from django import forms
from django.contrib import admin
from django.contrib.gis import admin as geo_admin
from django.utils.safestring import mark_safe
from django.core import urlresolvers
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist

from ..emailmgr.models import EmailAddress

from models import (Agency, AgencyUser, Alert, AlertLocation, MassAlert,
                    ChatMessage, UserProfile, SocialCrimeReport,
                    EntourageMember, Region, DispatchCenter,
                    Period, ClosedDate, StaticDevice, Theme,
                    EntourageSession, TrackingLocation, NamedLocation, UserNotification)


class UserNotificationAdmin(admin.ModelAdmin):
    model = UserNotification
    list_display = ['__unicode__', 'type', 'read', 'creation_date']
    search_fields = ['user__username', 'title', 'message',]
    raw_id_fields = ("user",)


class TrackingLocationInline(admin.StackedInline):
    model = TrackingLocation
    extra = 0


class NamedLocationAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'formatted_address',)
    search_fields = ['name', 'address',]


class EntourageSessionAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'user', 'status', 'entourage_notified',)
    list_filter = ('status',)
    list_select_related = ('status',)
    search_fields = ['user__username',]
    inlines = [TrackingLocationInline,]
    raw_id_fields = ("user",)


class EmailAddressInline(admin.StackedInline):
    model = EmailAddress
    extra = 0


class EntourageMemberAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'user', 'name', 'matched_user', 'phone_number', 'email_address')
    search_fields = ['user__username', 'name', 'phone_number', 'email_address',]
    raw_id_fields = ("matched_user", "user")


class EntourageMemberInline(admin.StackedInline):
    model = EntourageMember
    fk_name = 'user'
    extra = 0


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


class StaticDeviceAdmin(geo_admin.OSMGeoAdmin):
    model = StaticDevice
    list_display = ('__unicode__', 'uuid', 'type', 'description')
    list_filter = ('agency',)
    list_select_related = ('agency',)
    search_fields = ['agency__name', 'uuid', 'description', 'type',]


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


class AgencyAdmin(reversion_admin.VersionAdmin, geo_admin.OSMGeoAdmin):
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


class AgencyUserAdmin(admin.ModelAdmin):
    date_hierarchy = 'date_joined'
    list_display = ('__unicode__', 'agency', 'date_joined', 'device_type',
                    'email_verified', 'phone_number_verified',
                    'user_logged_in_via_social')
    list_filter = ('agency', 'groups', 'device_type',)
    list_select_related = ('agency',)
    search_fields = ['username', 'email', 'first_name', 'last_name']
    inlines = [
        EmailAddressInline,
        EntourageMemberInline,
    ]
    raw_id_fields = ("agency",)


class AlertLocationInline(admin.StackedInline):
    model = AlertLocation
    extra = 0


class AlertAdmin(reversion_admin.VersionAdmin):
    list_display = ('__unicode__', 'agency', 'agency_dispatcher', 'status',
                    'initiated_by', 'creation_date', 'last_modified', 'in_bounds')
    list_filter = ('agency', 'in_bounds', 'status', 'initiated_by', 'in_bounds')
    inlines = [
        AlertLocationInline,
    ]
    list_select_related = ('agency',)
    search_fields = ['agency_user__username', 'agency__name', 'static_device__uuid',]
    raw_id_fields = ("agency", "agency_user", 'agency_dispatcher', 'static_device')


class MassAlertAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'agency', 'agency_dispatcher',
                    'creation_date')
    list_filter = ('agency',)
    raw_id_fields = ("agency",)


class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'sender', 'message_sent_time',)
    search_fields = ['sender__username', 'alert__id', 'alert__agency__name',]
    raw_id_fields = ("sender", "alert")


class UserProfileAdmin(admin.ModelAdmin):
    search_fields = ['user__username',]


class SocialCrimeReportAdmin(geo_admin.OSMGeoAdmin):

    list_display = ('reporter', 'report_anonymous', 'report_type',
                    'last_modified', 'flagged_spam', 'flagged_by_dispatcher',
                    'viewed_time','viewed_by',)
    list_filter = ('report_anonymous', 'flagged_spam', 'report_type')
    list_select_related = ('reporter',)
    search_fields = ['reporter__username',]
    raw_id_fields = ("reporter", "flagged_by_dispatcher", "viewed_by")


class ThemeAdmin(admin.ModelAdmin):

    ordering = ['name',]

admin.site.register(Agency, AgencyAdmin)
admin.site.register(AgencyUser, AgencyUserAdmin)
admin.site.register(Alert, AlertAdmin)
admin.site.register(MassAlert, MassAlertAdmin)
admin.site.register(ChatMessage, ChatMessageAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(SocialCrimeReport, SocialCrimeReportAdmin)
admin.site.register(EntourageMember, EntourageMemberAdmin)
admin.site.register(DispatchCenter, DispatchCenterAdmin)
admin.site.register(StaticDevice, StaticDeviceAdmin)
admin.site.register(Theme, ThemeAdmin)

admin.site.register(EntourageSession, EntourageSessionAdmin)
admin.site.register(NamedLocation, NamedLocationAdmin)
admin.site.register(UserNotification, UserNotificationAdmin)