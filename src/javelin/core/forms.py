from django.forms import ModelForm

from .models import (Agency, StaticDevice)


class AgencySettingsForm(ModelForm):
    class Meta:
        model = Agency
        fields = ['enable_chat_autoresponder', 'chat_autoresponder_message', 'spot_crime_days_visible',]


class StaticDeviceForm(ModelForm):
    class Meta:
        model = StaticDevice
