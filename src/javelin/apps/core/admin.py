from django.contrib import admin
from django.contrib.gis import admin as gis_admin

from models import (Agency, AgencyUser, Alert, MassAlert,
                    ChatMessage, UserProfile)


class AgencyAdmin(gis_admin.GeoModelAdmin):
    pass


class AgencyUserAdmin(admin.ModelAdmin):
    pass


class AlertAdmin(admin.ModelAdmin):
    list_display = ('agency_user', 'creation_date', 'last_modified')


class MassAlertAdmin(admin.ModelAdmin):
    pass


class ChatMessageAdmin(admin.ModelAdmin):
    pass


class UserProfileAdmin(admin.ModelAdmin):
    pass


admin.site.register(Agency, AgencyAdmin)
admin.site.register(AgencyUser, AgencyUserAdmin)
admin.site.register(Alert, AlertAdmin)
admin.site.register(MassAlert, MassAlertAdmin)
admin.site.register(ChatMessage, ChatMessageAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
