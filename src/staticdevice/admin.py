from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin

# Register your models here.
from models import StaticDevice


class StaticDeviceAdmin(OSMGeoAdmin):
    model = StaticDevice
    list_display = ('__unicode__', 'uuid', 'type', 'description')
    list_filter = ('agency',)
    list_select_related = ('agency',)
    search_fields = ['agency__name', 'uuid', 'description', 'type',]


admin.site.register(StaticDevice, StaticDeviceAdmin)