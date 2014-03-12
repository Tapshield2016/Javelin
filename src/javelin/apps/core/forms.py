from django.forms import ModelForm

from .models import Agency


class AgencySettingsForm(ModelForm):
    class Meta:
        model = Agency
        fields = ['enable_chat_autoresponder', 'chat_autoresponder_message']
