from django.contrib import admin

from models import (Agency, AgencyUser, Alert, MassAlert,
                    ChatMessage, UserProfile)


class AgencyAdmin(admin.ModelAdmin):
    pass


class AgencyUserAdmin(admin.ModelAdmin):
    pass


class AlertAdmin(admin.ModelAdmin):
    pass


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
