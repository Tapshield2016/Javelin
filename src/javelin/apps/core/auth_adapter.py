from django.contrib.auth import get_user_model

from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from rest_framework.response import Response

from core.api.serializers.v1 import UserSerializer

User = get_user_model()


class SocialAuthAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # This isn't tested, but should work
        try:
            if sociallogin.account.user:
                user = User.objects.get(email=sociallogin.account.user.email)
                if not sociallogin.is_existing:
                    sociallogin.connect(request, user)
                # Create a response object
                resp = Response(UserSerializer(instance=user, context={'request': request}).data)
                raise ImmediateHttpResponse(resp)
        except User.DoesNotExist:
            pass
