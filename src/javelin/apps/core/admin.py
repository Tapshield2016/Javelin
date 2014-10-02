import reversion

from django import forms
from django.contrib import admin
from django.contrib.gis import admin as geo_admin
from django.utils.safestring import mark_safe
from django.core import urlresolvers

from emailmgr.models import EmailAddress

from models import (Agency, AgencyUser, Alert, AlertLocation, MassAlert,
                    ChatMessage, UserProfile, SocialCrimeReport,
                    EntourageMember, Region, DispatchCenter,
                    Period, ClosedDate, StaticDevice, Theme,)

class EmailAddressInline(admin.StackedInline):
    model = EmailAddress
    extra = 0

class EntourageMemberAdmin(admin.ModelAdmin):
    pass

class EntourageMemberInline(admin.StackedInline):
    model = EntourageMember
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


# class AgencyUserInlineForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         super(AgencyUserInlineForm, self).__init__(*args, **kwargs)
#         self.fields['groups'].queryset = AgencyUser.objects.filter(
#             group='Dispatchers')

class AgencyUserInline(admin.StackedInline):
    model = AgencyUser
    extra = 0
    fields = ('first_name', 'last_name', 'username', 'groups')

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super(AgencyUserInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
        field.queryset = field.queryset.filter(groups='Dispatchers')
        return field


class AgencyAdmin(reversion.VersionAdmin, geo_admin.OSMGeoAdmin):
    fieldsets = (
        ('General Settings', {
                'fields': (['name', 'domain', 'agency_point_of_contact',
                            'dispatcher_phone_number',
                            'dispatcher_secondary_phone_number',
                            'dispatcher_schedule_start',
                            'dispatcher_schedule_end', 'alert_mode_name',
                            'alert_completed_message', 'sns_primary_topic_arn',
                            'require_domain_emails', 'display_command_alert',
                            'loop_alert_sound',
                            'launch_call_to_dispatcher_on_alert',
                            'show_agency_name_in_app_navbar',
                            'enable_chat_autoresponder',
                            'chat_autoresponder_message',
                            'enable_user_location_requests',
                            'spot_crime_days_visible',])
        }),
        ('Agency Location and Boundaries', {
                'fields': (['agency_boundaries', 'agency_center_from_boundaries', 'agency_center_latitude',
                            'agency_center_longitude', 'agency_center_point', 'agency_radius',
                            'default_map_zoom_level']),
        }),
        ('Agency Theme', {
                'fields': (['theme', 'theme_link', 'branding', 'branding_link', 'agency_logo', 'agency_alternate_logo',
                            'agency_small_logo', 'agency_theme']),
        }),
        ('Agency Optional Info', {
                'fields': (['agency_info_url', 'agency_rss_url',]),
        }),
        ('Available Services', {
                'fields': (['crime_reports_available', 'emergency_call_available', 'alert_available',
                            'chat_available', 'yank_available', 'entourage_available',
                            'static_device_available', 'mass_alert_available',]),
        }),
    )
    inlines = [
        RegionInline, DispatchCenterInline, AgencyUserInline, StaticDeviceInline,
    ]
    readonly_fields = ['theme_link', 'branding_link',]

    def get_form(self, request, obj=None, **kwargs):
        # just save obj reference for future processing in Inline
        request._obj_ = obj
        return super(AgencyAdmin, self).get_form(request, obj, **kwargs)

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


class AlertLocationInline(admin.StackedInline):
    model = AlertLocation
    extra = 0


class AlertAdmin(reversion.VersionAdmin):
    list_display = ('__unicode__', 'agency', 'status', 'creation_date', 'last_modified')
    list_filter = ('agency', 'status')
    inlines = [
        AlertLocationInline,
    ]
    list_select_related = ('agency',)
    search_fields = ['agency_user__username', 'agency__name', 'static_device__uuid',]


class MassAlertAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'agency', 'agency_dispatcher',
                    'creation_date')
    list_filter = ('agency',)


class ChatMessageAdmin(admin.ModelAdmin):
    pass


class UserProfileAdmin(admin.ModelAdmin):
    pass


class SocialCrimeReportAdmin(geo_admin.OSMGeoAdmin):

    list_display = ('reporter', 'report_anonymous', 'report_type',
                    'last_modified', 'flagged_spam', 'flagged_by_dispatcher',
                    'viewed_time','viewed_by',)
    list_filter = ('report_anonymous', 'flagged_spam', 'report_type')
    list_select_related = ('reporter',)
    search_fields = ['reporter__username',]

class ThemeAdmin(admin.ModelAdmin):
    pass

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