from reversion import admin as reversion_admin

from django.contrib import admin
from django.contrib.gis import admin as geo_admin

from emailmgr.models import EmailAddress

from models import (AgencyUser, Alert, AlertLocation, MassAlert,
                    ChatMessage, UserProfile, SocialCrimeReport,
                    EntourageMember, EntourageSession, TrackingLocation,
                    NamedLocation, UserNotification)


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


admin.site.register(AgencyUser, AgencyUserAdmin)
admin.site.register(Alert, AlertAdmin)
admin.site.register(MassAlert, MassAlertAdmin)
admin.site.register(ChatMessage, ChatMessageAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(SocialCrimeReport, SocialCrimeReportAdmin)
admin.site.register(EntourageMember, EntourageMemberAdmin)

admin.site.register(EntourageSession, EntourageSessionAdmin)
admin.site.register(NamedLocation, NamedLocationAdmin)
admin.site.register(UserNotification, UserNotificationAdmin)