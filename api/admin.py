from django.contrib import admin

# Register your models here.
from api.models import Device


class DeviceListAdmin(admin.ModelAdmin):
    list_display = ['id', 'status']
    list_filter = ['status']




admin.site.register(Device, DeviceListAdmin)