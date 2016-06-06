from models import EmailAddress

from rest_framework import serializers, viewsets


class EmailAddressGETSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmailAddress
        fields = ('email', 'is_primary', 'is_active', 'is_activation_sent',)


class EmailAddressUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmailAddress


class EmailAddressViewSet(viewsets.ModelViewSet):
    queryset = EmailAddress.objects.select_related('user').all()
    model = EmailAddress
    # filter_fields = ('user',)
    # serializer_class = EmailAddressGETSerializer








