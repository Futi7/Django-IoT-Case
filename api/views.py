from datetime import datetime, timedelta

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
import json

# 'api_view' decorator is for method allowances
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Device, Log
from .serializers import DeviceSerializer


@api_view(['GET'])
def api_doc(request):
    api_urls = {
        'List': '/device-list/',
        'Details': '/device-device_detail/<int:id>',
        'Status Update': '/device-status-update/<int:id>',
        'Show Status Percentage':'/device-status-percentage/<int:id>',

    }
    return Response(api_urls)

# TODO DEVİCE = get_object_or_404(DEV, pk=device_id)

@api_view(['GET'])
def device_list(request):
    devices = Device.objects.all()
    response = {device.id: {"Status": device.status} for device in devices}
    response = json.dumps(response)

    return Response(json.loads(response))


@api_view(['GET'])
def device_detail(request, id):
    devices = get_object_or_404(Device, pk=id)
    serializer = DeviceSerializer(devices, many=False)
    return Response(serializer.data)


@api_view(['POST'])
def device_status_update(request, id):
    device = get_object_or_404(Device, pk=id)
    if device.status != request.data['status']:
        new_log_entry = Log()
        new_log_entry.device = device
        new_log_entry.status = request.data['status']
        new_log_entry.save()
    serializer = DeviceSerializer(instance=device, data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)


@api_view(['POST', 'GET'])
def device_status_percentage(request, id):
    """
    status_control is to check if last log data's status whether online or offline
    offline_time variable is for calculating the total offline time
    """
    status_control = 'ONLINE'
    offline_time = 0

    #Get post data from request then assign them
    start_date = datetime.strptime(request.data['start_date'], "%Y-%m-%d %H:%M")
    end_date = datetime.strptime(request.data['end_date'], "%Y-%m-%d %H:%M")

    #calculate the time interval between prompted dates
    time_interval = round((end_date - start_date).total_seconds() / 60.0, 2)

    device_logs = Log.objects.filter(time_stamp__gte=start_date, time_stamp__lte=end_date, device=2).order_by(
        'time_stamp')

    timeline = dict()
    temp_online_time = start_date
    for log in device_logs:
        if log.status == 'ONLINE':
            offline_time += (log.time_stamp - start_date).total_seconds() / 60.0
            temp_online_time = log.time_stamp
            status_control = 'ONLINE'
            timeline.update({("(%.19s)-(%.19s)" % (start_date, log.time_stamp)): log.status})

        else:
            timeline.update({("(%.19s)-(%.19s)" % (temp_online_time, log.time_stamp)): log.status})
            start_date = log.time_stamp
            status_control = 'OFFLINE'

    """
    Check the last log status to add timeline and calculate the time interval between end date and last log if its offline
    
    """
    if status_control == 'ONLINE':
        timeline.update({("(%.19s)-(%.19s)" % (start_date, end_date)): "ONLINE"})
        offline_time += ((end_date - start_date).total_seconds() / 60.0)
    else:
        timeline.update({("(%.19s)-(%.19s)" % (temp_online_time, end_date)): "OFFLINE"})


    offline_percentage = round((offline_time / time_interval) * 100, 2)
    online_percentage = round(100 - offline_percentage, 2)

    return Response({
        'timeline': timeline,
        'report': {
        'ONLINE': '%'+str(online_percentage),
        'OFFLINE': '%'+str(offline_percentage),
        }
})
