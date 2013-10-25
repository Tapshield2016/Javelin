from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.sites.models import get_current_site

from registration.models import RegistrationProfile

from rest_framework import status, serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response

from serializers.v1 import UserSerializer


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
