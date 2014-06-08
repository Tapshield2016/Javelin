from models import EmailAddress
from django.contrib import admin


class EmailAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'is_active', 'is_primary', 'identifier',)
    search_fields = ['user__username', 'email', 'identifier',]
    list_per_page = 25

admin.site.register(EmailAddress, EmailAddressAdmin)
