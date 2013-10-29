import datetime

from django.contrib.auth import (authenticate, get_user_model,
                                 login as auth_login)
from django.contrib.auth.models import Group
from django.contrib.sites.models import get_current_site
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import ensure_csrf_cookie

from registration.models import RegistrationProfile

from rest_framework import status, serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response

from serializers.v1 import UserSerializer

User = get_user_model()


@api_view(['POST'])
def register_user(request):
    serialized = UserSerializer(data=request.DATA)
    if serialized.is_valid():
        user = RegistrationProfile.objects.create_inactive_user(
            serialized.init_data['email'],
            serialized.init_data['username'],
            serialized.init_data['password'],
            get_current_site(request),
        )
        user_group = Group.objects.get(name='Users')
        user.groups.add(user_group)
        return Response(UserSerializer(instance=user).data,
                        status=status.HTTP_201_CREATED)
    else:
        return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def resend_verification_email(request):
    email = request.DATA.get('email', None)
    if email:
        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                profile = RegistrationProfile.objects.get(user=user)
                if profile.activation_key_expired():
                    profile.delete()
                    profile = RegistrationProfile.objects.create_profile(user)
                profile.send_activation_email(get_current_site(request))
                user.date_joined = datetime.datetime.now()
                user.save()
            else:
                return Response("User has already been activated",
                                status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist, RegistrationProfile.DoesNotExist:
            return Response("User not found",
                            status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response("Email required.",
                        status=status.HTTP_400_BAD_REQUEST)
    return Response("Ok.", status=status.HTTP_200_OK)


@ensure_csrf_cookie
def login(request):
    login_failed = False
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                auth_login(request, user)
            else:
                return HttpResponseForbidden(\
                    content='Your account is not active.')
        else:
            login_failed = True

    if request.user.is_authenticated():
        status = 200
        message = "Authenticated."
    else:
        status = 401
        message = "Authorization required."

    response = HttpResponse(content=message)
    response.status_code = status

    if login_failed:
        response['Auth-Response'] = 'Login failed'

    return response
