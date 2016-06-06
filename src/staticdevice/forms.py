from django.forms import ModelForm

from models import StaticDevice


class StaticDeviceForm(ModelForm):
    class Meta:
        model = StaticDevice
        fields = '__all__'
