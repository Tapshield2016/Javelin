from django.contrib import admin

from models import Agency, AgencyUser, UserProfile


class AgencyAdmin(admin.ModelAdmin):
    pass


class AgencyUserAdmin(admin.ModelAdmin):
    pass


class UserProfileAdmin(admin.ModelAdmin):
    pass


admin.site.register(Agency, AgencyAdmin)
admin.site.register(AgencyUser, AgencyUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
