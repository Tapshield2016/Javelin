from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from core.api.serializers.v1 import UserSerializer


@login_required(login_url='shieldcommand-login')
def index(request):
    if not request.user.is_superuser:
        if request.user.groups.filter(name='Dispatchers').count() == 0:
            raise Http404
    site = get_current_site(request)
    agency = request.user.agency
    agency_boundaries_coords = []
    multi_region_boundaries = []
    user = UserSerializer(request.user)
    region = agency.region

    if agency.region.all():
        for region in agency.region:
            region_boundaries_coord = []
            for coord in region.boundaries:
                lat, long = coord.split(',')
                region_boundaries_coord.append((lat, long))
            multi_region_boundaries.append(region_boundaries_coord)

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
                                   settings.SHIELD_COMMAND_API_VERSION,
                               "region_boundaries": multi_region_boundaries,
                               "user": user.data},
                              context_instance=RequestContext(request))
