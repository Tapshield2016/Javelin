import datetime
import json

from django.conf import settings
from django.contrib.auth import (authenticate, get_user_model,
                                 login as auth_login)
from django.contrib.auth.models import Group
from django.contrib.sites.models import get_current_site
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt

from registration.models import RegistrationProfile

from rest_framework import status, serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response

from twilio.util import TwilioCapability

from models import Agency
from api.serializers.v1 import UserSerializer

User = get_user_model()


@api_view(['POST'])
def register_user(request):
    request_data = request.DATA.copy()
    agency_id = request_data.get('agency', None)
    if agency_id:
        del request_data['agency']
    try:
        agency = Agency.objects.get(pk=agency_id)
    except Agency.DoesNotExist:
        agency_id = None

    if not 'username' in request_data:
        request_data['username'] = request_data.get('email', None)

    serialized = UserSerializer(data=request_data)
    if serialized.is_valid() and agency_id:
        user = RegistrationProfile.objects.create_inactive_user(
            serialized.init_data['email'].lower(),
            serialized.init_data['username'].lower(),
            serialized.init_data['password'],
            get_current_site(request),
        )
        user_group = Group.objects.get(name='Users')
        user.groups.add(user_group)
        user.agency = agency
        user.phone_number = request_data.get('phone_number', '')
        user.disarm_code = request_data.get('disarm_code', '')
        user.first_name = request_data.get('first_name', '')
        user.last_name = request_data.get('last_name', '')
        user.save()
        return Response(UserSerializer(instance=user).data,
                        status=status.HTTP_201_CREATED)
    else:
        return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def resend_verification_email(request):
    email = request.DATA.get('email', None)
    message = "Ok"
    response_status = status.HTTP_200_OK
    if email:
        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                try:
                    profile = RegistrationProfile.objects.get(user=user)
                    if profile.activation_key_expired():
                        profile.delete()
                        profile =\
                            RegistrationProfile.objects.create_profile(user)
                    profile.send_activation_email(get_current_site(request))
                    user.date_joined = datetime.datetime.now()
                    user.save()
                except RegistrationProfile.DoesNotExist:
                    message = "No registration profile found for user."
                    response_status = status.HTTP_400_BAD_REQUEST
            else:
                message = "User has already been activated"
                response_status = status.HTTP_400_BAD_REQUEST
        except User.DoesNotExist, RegistrationProfile.DoesNotExist:
            message = "User not found"
            response_status = status.HTTP_400_BAD_REQUEST
    else:
        message = "Email required"
        response_status = status.HTTP_400_BAD_REQUEST
    return Response({"message": message}, status=response_status)


@csrf_exempt
def login(request):
    login_failed = False
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active and user.email_verified:
                auth_login(request, user)
            else:
                if not user.email_verified:
                    response = HttpResponse(content='User email address has not been verified')
                    response.status_code = 401
                    response['Auth-Response'] = 'Email unverified'
                    return response
                if not user.is_active:
                    return HttpResponseForbidden(\
                        content='Your account is not active.')
        else:
            login_failed = True

    if request.user.is_authenticated():
        status = 200
        serialized = UserSerializer(request.user, context={'request': request})
        message = json.dumps(serialized.data)
    else:
        status = 401
        message = "Authorization required."

    response = HttpResponse(content=message)
    response.status_code = status
    if status == 200:
        response.content_type = 'application/json'

    if login_failed:
        response['Auth-Response'] = 'Login failed'

    return response


@api_view(['GET'])
def verified(request):
    user_email = request.GET.get('email', None)
    message = ''
    if user_email:
        try:
            user = User.objects.get(email=user_email)
            message = user.email_verified
            return Response({'message': message})
        except User.DoesNotExist:
            message = 'user not found'
        except ValueError:
            message = 'user must be an integer'
    else:
        message = 'user is a required parameters'
    return Response({'message': message},
                    status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def twilio_call_token(request):
    capability = TwilioCapability(settings.TWILIO_ACCOUNT_SID,
                                  settings.TWILIO_AUTH_TOKEN)
    capability.allow_client_outgoing(settings.TWILIO_APP_SID)
    return Response({'token': capability.generate(expires=60 * 120)},
                    status=status.HTTP_200_OK)
