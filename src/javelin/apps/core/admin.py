import reversion

from django.contrib import admin
from django.contrib.gis import admin as geo_admin

from models import (Agency, AgencyUser, Alert, AlertLocation, MassAlert,
                    ChatMessage, UserProfile, SocialCrimeReport,
                    EntourageMember, Region, DispatchCenter,
                    Period, ClosedDate,)


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

class DispatchCenterAdmin(admin.ModelAdmin):
    inlines = [ClosedDateInline, PeriodInline]

class RegionInline(admin.StackedInline):
    model = Region
    extra = 0

class DispatchCenterInline(admin.StackedInline):
    model = DispatchCenter
    extra = 0
    fields = ('name', 'phone_number', 'changeform_link')
    readonly_fields = ('changeform_link', )


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
                'fields': (['agency_logo', 'agency_alternate_logo',
                            'agency_small_logo', 'agency_theme']),
        }),
        ('Agency Optional Info', {
                'fields': (['agency_info_url', 'agency_rss_url',]),
        }),
    )
    inlines = [
        RegionInline, DispatchCenterInline,
    ]

class AgencyUserAdmin(admin.ModelAdmin):
    date_hierarchy = 'date_joined'
    list_display = ('__unicode__', 'agency', 'date_joined', 'device_type',
                    'email_verified', 'phone_number_verified',
                    'user_logged_in_via_social')
    list_filter = ('agency', 'groups', 'device_type',)
    list_select_related = ('agency',)
    search_fields = ['email', 'first_name', 'last_name']
    inlines = [
        EntourageMemberInline,
    ]


class AlertLocationInline(admin.StackedInline):
    model = AlertLocation
    extra = 0


class AlertAdmin(reversion.VersionAdmin):
    list_display = ('agency_user', 'creation_date', 'last_modified')
    list_filter = ('agency', 'status')
    inlines = [
        AlertLocationInline,
    ]


class MassAlertAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'agency', 'agency_dispatcher',
                    'creation_date')
    list_filter = ('agency',)


class ChatMessageAdmin(admin.ModelAdmin):
    pass


class UserProfileAdmin(admin.ModelAdmin):
    pass


class SocialCrimeReportAdmin(geo_admin.OSMGeoAdmin):
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