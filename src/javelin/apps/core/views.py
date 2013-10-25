import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.sites.models import get_current_site

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
