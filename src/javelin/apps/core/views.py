from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from rest_framework import status, serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response

from serializers.v1 import UserSerializer


@api_view(['POST'])
def register_user(request):
    VALID_USER_FIELDS = [f.name for f in get_user_model()._meta.fields]
    DEFAULTS = {
        # we could provide field defaults here if needed...
    }

    serialized = UserSerializer(data=request.DATA)
    if serialized.is_valid():
        user_data = {field: data for (field, data) in request.DATA.items()\
                         if field in VALID_USER_FIELDS}
        user_data.update(DEFAULTS)
        user = get_user_model().objects.create_user(
            **user_data
        )
        user_group = Group.objects.get(name='Users')
        user.groups.add(user_group)
        return Response(UserSerializer(instance=user).data,
                        status=status.HTTP_201_CREATED)
    else:
        return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)
