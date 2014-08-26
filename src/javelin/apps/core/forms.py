from django.forms import ModelForm

from .models import (Agency, TalkaphoneDevice)


class AgencySettingsForm(ModelForm):
    class Meta:
        model = Agency
        fields = ['enable_chat_autoresponder', 'chat_autoresponder_message', 'spot_crime_days_visible',]

class TalkaphoneDeviceForm(ModelForm):
    class Meta:
        model = TalkaphoneDevice
