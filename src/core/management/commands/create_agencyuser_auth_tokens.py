from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from rest_framework.authtoken.models import Token

User = get_user_model()


class Command(BaseCommand):

    def handle(self, *args, **options):
        for user in User.objects.all():
            Token.objects.get_or_create(user=user)
