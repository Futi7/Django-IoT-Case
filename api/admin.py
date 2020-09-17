from django.contrib import admin

# Register your models here.
from api.models import Device, Log


class DeviceListAdmin(admin.ModelAdmin):
    list_display = ['id', 'status']
    list_filter = ['status']

class LogListAdmin(admin.ModelAdmin):
    list_display = ['time_stamp', 'device_id', 'status']
    list_filter = ['device_id', 'status']


admin.site.register(Device, DeviceListAdmin)
admin.site.register(Log, LogListAdmin)
