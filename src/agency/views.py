from django.shortcuts import render
from agency.forms import AgencySettingsForm
from django.http import (
    HttpResponse,
    Http404,
    HttpResponseRedirect
)
from models import Agency
from django.core.urlresolvers import reverse


def agency_settings_form(request):
    if request.method == 'POST':
        agency_id = request.POST.get('agency_id', None)
        if not agency_id:
            raise Http404
        try:
            agency_id = int(agency_id)
            agency = Agency.objects.get(pk=int(agency_id))
        except Agency.DoesNotExist:
            raise Http404
        form = AgencySettingsForm(request.POST, instance=agency)
        if form.is_valid():
            form.save()
            if request.is_ajax():
                return HttpResponse("OK")
            else:
                return HttpResponseRedirect("%s?agency_id=%d" % (reverse('agency_settings'), agency_id))
    else:
        agency_id = request.GET.get('agency_id', None)
        if not agency_id:
            raise Http404
        try:
            agency = Agency.objects.get(pk=int(agency_id))
        except Agency.DoesNotExist:
            raise Http404
        form = AgencySettingsForm(instance=agency)
    return render(request, 'agency_settings_form.html',
                  {'form': form})