from django.shortcuts import render
from forms import StaticDeviceForm
from models import StaticDevice

from django.shortcuts import get_object_or_404

from django.http import  HttpResponse

from core.api.serializers.v1 import (
    StaticDeviceSerializer,
    UserSerializer,
    AgencySerializer,
    AlertSerializer,
)

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.settings import api_settings

from core.tasks import new_static_alert
from core.utils import group_required, get_agency_from_unknown

from core.models import Alert


def serialize_static_device_save(request):
    request_data = request.POST.copy()
    request_data['user'] = UserSerializer(request.user, context={'request': request}).data['url']
    agency_id = request_data.get('agency', None)

    agency = None
    if agency_id:
        agency = get_agency_from_unknown(agency_id)
    if agency:
        request_data['agency'] = AgencySerializer(agency, context={'request': request}).data['url']

    serializer = StaticDeviceSerializer(data=request_data, context={'request': request})

    if not serializer.is_valid():
        return serializer

    serializer.save()

    if not serializer.object.agency:
        serializer.object.delete()
        serializer.errors['agency'] = [u'No agency could be found from the given parameters.']
        return serializer

    return serializer


@api_view(['POST'])
@group_required('Device Maker', )
def register_static_device(request):
    """Registers new Static devices with the API

    uuid -- (Required) Unique identifier of the device (serial number or randomly generated string)
    type -- (Optional) Model number or device type
    description -- (Optional) Human readable identifier denoting location (e.g. building, street, landmark, etc.)
    agency -- (Required) Numerical ID of the agency (agency = organization receiving alerts)
    latitude -- (Required) Latitude coordinate value
    longitude -- (Required) Longitude coordinate value
    """

    if request.method == 'POST':

        serializer = serialize_static_device_save(request)

        if serializer.errors:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        headers = {}
        try:
            headers = {'Location': serializer.data[api_settings.URL_FIELD_NAME]}
        except (TypeError, KeyError):
            pass
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    else:

        response = HttpResponse(content="Request method not allowed")
        response.status_code = 405

    return response


@api_view(['POST'])
@group_required('Device Maker', )
def static_alert(request):
    """Send a Static alert to dispatchers

    uuid -- (Required) Unique identifier of the device (serial number or randomly generated string)
    type -- (Optional) Model number or device type
    description -- (Optional) Human readable identifier denoting location (e.g. building, street, landmark, etc.)
    agency -- (Optional) Numerical ID of the agency (agency = organization receiving alerts)
    latitude -- (Required) Latitude coordinate value
    longitude -- (Required) Longitude coordinate value
    """

    if request.method == 'POST':
        request_post = request.POST.copy()
        uuid = request.POST.get('uuid')

        if not uuid:
            response = HttpResponse(content="Must contain 'uuid' parameter")
            response.status_code = 400
            return response

        device = None

        try:
            device = StaticDevice.objects.get(uuid=uuid)
        except:
            pass

        if not device:
            serializer = serialize_static_device_save(request)
            if serializer.errors:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            device = serializer.object

        current_device, created = StaticDevice.objects.get_or_create(uuid=uuid)
        form = StaticDeviceForm(request_post, instance=current_device)
        if form.is_valid():
            form.save()

        if not current_device.agency:
            current_device.delete()
            response = HttpResponse(content="Could not find agency")
            response.status_code = 404

        elif not current_device.location_point:
            response = HttpResponse(content="No location provided")
            response.status_code = 400

        else:
            response = HttpResponse(content="Created")
            response.status_code = 201
            alert = new_static_alert(current_device)
            serializer = AlertSerializer(instance=alert, context={'request': request})

            headers = {}
            try:
                headers = {'Location': serializer.data[api_settings.URL_FIELD_NAME]}
            except (TypeError, KeyError):
                pass
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)

    else:
        response = HttpResponse(content="Request method not allowed")
        response.status_code = 405

    return response


@api_view(['POST'])
@group_required('Device Maker', )
def static_disarm(request):
    if request.method == 'POST':
        uuid = request.POST.get('uuid')

        if not uuid:
            response = HttpResponse(content="Must contain 'uuid' parameter")
            response.status_code = 400
            return response

        # current_device, created = StaticDevice.objects.get (uuid=uuid)
        current_device = get_object_or_404(StaticDevice, uuid=uuid)

        active_alerts = Alert.active.filter(static_device=current_device)
        if active_alerts:
            alert = active_alerts[0]
            alert.disarm()
            serializer = AlertSerializer(instance=alert, context={'request': request})

            headers = {}
            try:
                headers = {'Location': serializer.data[api_settings.URL_FIELD_NAME]}
            except (TypeError, KeyError):
                pass
            return Response(serializer.data, status=status.HTTP_200_OK,
                            headers=headers)

        else:
            response = HttpResponse(content="Alert not found")
            response.status_code = 404

    else:
        response = HttpResponse(content="Request method not allowed")
        response.status_code = 405

    return response


def static_device_form(request):
    response = HttpResponse(content="Not available at this time")
    response.status_code = 404
    return response

    # if request.method == 'GET':
    #     form = StaticDeviceForm()
    # else:
    #     # A POST request: Handle Form Upload
    #     form = StaticDeviceForm(request.POST) # Bind data from request.POST into a PostForm
    #
    #     # If data is valid, proceeds to create a new post and redirect the user
    #     if form.is_valid():
    #         device = form.save()
    #         return HttpResponseRedirect(reverse('static_device_details',
    #                                             args=(device.uuid,)))
    #         # return HttpResponseRedirect("%s%d" % (reverse('static_device_details'), device.id))

    # return render(request, 'core/forms/static_device_form.html', {
    #     'form': form,
    # })