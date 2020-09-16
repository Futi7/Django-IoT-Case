from datetime import datetime, timedelta

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404

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
    serializer = DeviceSerializer(devices, many=True)
    return Response({"data":serializer.data})


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
    start_date = '2020-09-16 18:00' #request.data['start_date']
    end_date = '2020-09-15 19:10' #request.data['end_date']

    device_logs = Log.objects.filter(time_stamp__gte=start_date, time_stamp__lte=end_date, device=id).order_by('-time_stamp')
    for dev in device_logs:
        pass


    online_percentage = 3
    offline_percentage = 7

    return Response({'ONLINE': '%'+str(online_percentage),
                     'OFFLINE': '%'+str(offline_percentage),
                     'devices': device_logs})

def test(request):
    """
    log1 = Log.objects.get(id=1)
    log2 = Log.objects.get(id=2)
    time_diff = log2.time_stamp - log1.time_stamp

    print(log1.time_stamp.__repr__())

    print(time_diff)
   """
    control = 0
    start_date = datetime.strptime('2020-09-16 18:00', "%Y-%m-%d %H:%M")  # request.data['start_date']
    end_date = datetime.strptime('2020-09-16 19:10', "%Y-%m-%d %H:%M")  # request.data['end_date']
    print(start_date)
    total_time = (end_date - start_date).total_seconds() / 60.0
    total_time = round(total_time, 2)
    offline_time = 0
    device_logs = Log.objects.filter(time_stamp__gte=start_date, time_stamp__lte=end_date, device=2).order_by(
        'time_stamp')



    for device_log in device_logs:
        if device_log.status == 'ONLINE':
            offline_time += (device_log.time_stamp - start_date).total_seconds() / 60.0
        else:
            start_date = device_log.time_stamp
            control = 1

    if control == 1:
        offline_time += ((end_date - start_date).total_seconds() / 60.0)


    offline_time = round(offline_time, 2)
    print(offline_time)
    print(total_time)
    offline_percentage = offline_time / total_time

    print(offline_percentage)


    return HttpResponse("test")
