from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext


@login_required(login_url='shieldcommand-login')
def index(request):
    site = get_current_site(request)
    agency = request.user.agency
    agency_boundaries_coords = []
    if agency.agency_boundaries:
        agency_boundaries_list = eval(agency.agency_boundaries)
        for coord in agency_boundaries_list:
            lat, long = coord.split(',')
            agency_boundaries_coords.append((lat, long))
    auth_token = request.user.auth_token
    return render_to_response('shieldcommand/index.html',
                              {"agency": agency,
                               "agency_boundaries": agency_boundaries_coords,
                               "auth_token": auth_token,
                               "api_version":\
                                   settings.SHIELD_COMMAND_API_VERSION},
                              context_instance=RequestContext(request))
