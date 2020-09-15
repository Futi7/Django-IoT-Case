from django.db import models


class Device(models.Model):
    STATUS = (
        ('OFFLINE', 'Offline'),
        ('ONLINE', 'Online'),
    )
    status = models.CharField(max_length=10, default="OFFLINE", choices=STATUS)


class Log(models.Model):
    status = models.CharField(max_length=10)
    time_stamp = models.DateTimeField(auto_now_add=True)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
