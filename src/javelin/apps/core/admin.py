import reversion

from django.contrib import admin
from django.contrib.gis import admin as geo_admin

from models import (Agency, AgencyUser, Alert, AlertLocation, MassAlert,
                    ChatMessage, UserProfile, SocialCrimeReport)


class AgencyAdmin(reversion.VersionAdmin, geo_admin.OSMGeoAdmin):
    pass


class AgencyUserAdmin(admin.ModelAdmin):
    date_hierarchy = 'date_joined'
    list_display = ('email', 'agency', 'date_joined', 'device_type',
                    'email_verified', 'phone_number_verified')
    list_filter = ('agency', 'groups', 'device_type',)
    list_select_related = ('agency',)
    search_fields = ['email', 'first_name', 'last_name']


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
    pass


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
