from datetime import datetime
import json

from django.shortcuts import get_object_or_404

"""
 'api_view' decorator is for method allowances
 'status' import is for responding status errors
"""
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAdminUser

from .models import Device, Log
from .serializers import DeviceSerializer


@api_view(['GET'])
def api_doc(request):
    """
    This is a simple api documentation
    """
    api_urls = {
        'List': {
            'URL': '/device-list/',
            'Description': 'List all devices',
            'Allowed Methods': '[GET]',
            'Authentication': 'Required',
            'JSON Body Format': 'None'
        },
        'Details': {
            'URL': '/device_detail/<int:device_id>/',
            'Description': 'Show the device info',
            'Allowed Methods': '[GET]',
            'Authentication': 'Required',
            'JSON Body Format': 'None'
        },
        'Status Update': {
            'URL': '/device-status-update/<int:device_id>/',
            'Description': 'List all devices',
            'Allowed Methods': '[POST]',
            'Authentication': 'Required',
            'JSON Body Format': {'status': 'value'}
        },
        'Show Status Percentage': {
            'URL': '/device-status-percentage/<int:device_id>/',
            'Description': 'List all devices',
            'Allowed Methods': '[GET, POST]',
            'Authentication': 'Required',
            'JSON Body Format': {'start_date': 'YY-mm-DD HH:MM', 'end_date': 'YY-mm-DD HH:MM'}
        },
    }
    return Response(api_urls)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAdminUser])
def device_list(request):
    devices = Device.objects.all()
    """ 
    This is a custom serializer designed simply with 'Dict Comprehension'
    Built-in serializer's return format is 'JSONArray' instead of 'JSON'
    Uncomment below code to use built-in serializer
    """

    """
    devices_json = DeviceSerializer(devices, many=True)
    return Response({"Devices": devices_json.data})
    """

    devices_json = json.dumps({device.id: {"Status": device.status} for device in devices})
    return Response({"Devices": json.loads(devices_json)})


@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAdminUser])
def device_detail(request, device_id):
    """
    'get_object_or_404 checks for the prompted data
    returns the data if its available, raises 404 status code if its not.
    """

    devices = get_object_or_404(Device, pk=device_id)
    serializer = DeviceSerializer(devices, many=False)
    return Response(serializer.data)


@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAdminUser])
def device_status_update(request, device_id):
    # Below 'try/catch' block is for returning an error response when a non-proper data posted
    try:
        data_status = request.data['status']
    except KeyError:
        return Response({"status": 422, "details": "Invalid key.Enter a status."},
                        status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    """
    In below if statement we are checking if posted status data is valid via 
    our 'is_valid_status()' function and return a proper response if its invalid
    """
    if not is_valid_status(data_status):
        return Response({"status": 422, "details": "Invalid status format try as 'ONLINE' or 'OFFLINE' "},
                        status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    device = get_object_or_404(Device, pk=device_id)

    # Below if statement checks if there is a difference between current device state and posted status
    if device.status != request.data['status']:
        new_log_entry = Log()
        new_log_entry.device = device
        new_log_entry.status = request.data['status']
        new_log_entry.save()

    # This is a rest framework built-in serializer
    serializer = DeviceSerializer(instance=device, data=request.data)
    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(['POST', 'GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAdminUser])
def device_status_percentage(request, device_id):
    try:
        Device.objects.get(pk=device_id)
    except Device.DoesNotExist:
        return Response({"status": 404, "details": "Invalid device."},
                        status=status.HTTP_404_NOT_FOUND)

    """
    status_control is to check if last log data's status whether online or offline
    offline_time variable is for calculating the total offline time
    timeline dictionary is for keeping the records of logs
    PRECISION constant determines the float precision.
    """
    status_control = 'ONLINE'
    offline_time = 0
    timeline = dict()
    PRECISION = 2


    # Get post data from request then assign them
    start_date = datetime.strptime(request.data['start_date'], "%Y-%m-%d %H:%M")
    end_date = datetime.strptime(request.data['end_date'], "%Y-%m-%d %H:%M")

    # Calculate the time interval between prompted dates
    time_interval = round((end_date - start_date).total_seconds() / 60.0, 2)
    device_logs = Log.objects.filter(time_stamp__gte=start_date, time_stamp__lte=end_date, device=device_id).order_by(
        'time_stamp')

    if device_logs.exists():
        """
        In the below loop we are calculating the total offline time
        and record logs
        """
        temp_online_time = start_date
        for log in device_logs:
            if log.status == 'ONLINE':
                offline_time += (log.time_stamp - start_date).total_seconds() / 60.0
                temp_online_time = log.time_stamp
                status_control = 'ONLINE'
                timeline.update({("(%.19s)-(%.19s)" % (start_date, log.time_stamp)): "OFFLINE"})

            else:
                timeline.update({("(%.19s)-(%.19s)" % (temp_online_time, log.time_stamp)): "ONLINE"})
                start_date = log.time_stamp
                status_control = 'OFFLINE'

        """
        Check the last log status to add timeline
        Calculate the time interval between end date and last log if its offline
        The algorithm calculates offline time percentage then get online time percentage from it
        """
        if status_control == 'OFFLINE':
            timeline.update({("(%.19s)-(%.19s)" % (start_date, end_date)): "OFFLINE"})
            offline_time += ((end_date - start_date).total_seconds() / 60.0)

        else:
            timeline.update({("(%.19s)-(%.19s)" % (temp_online_time, end_date)): "ONLINE"})

        offline_percentage = round((offline_time / time_interval) * 100, PRECISION)
        online_percentage = round(100 - offline_percentage, PRECISION)

    # If there is no record check devices current state then return that value
    else:
        return Response({
            'timeline': "There is no record between given dates.",
            'report': {
                'ONLINE': '%0',
                'OFFLINE': '%100 DEFAULT',
            }
        })

    return Response({
        'timeline': timeline,
        'report': {
            'ONLINE': '%' + str(online_percentage),
            'OFFLINE': '%' + str(offline_percentage),
        }
    })


def is_valid_status(data_status):
    if data_status in ['ONLINE', 'OFFLINE']:
        return True
    return False


def is_valid_date(data_date):
    date_format = "%Y-%m-%d %H:%i"
    try:
        datetime.strptime(data_date, date_format)
    except ValueError:
        return False
    return True
