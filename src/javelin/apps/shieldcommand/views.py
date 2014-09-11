from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from core.api.serializers.v1 import UserSerializer, ThemeSerializer


@login_required(login_url='shieldcommand-login')
def index(request):
    if not request.user.is_superuser:
        if request.user.groups.filter(name='Dispatchers').count() == 0:
            return render_to_response('shieldcommand/unauthorized.html',
                                      context_instance=RequestContext(request))
    site = get_current_site(request)
    agency = request.user.agency
    agency_boundaries_coords = []
    multi_region_boundaries = []
    user = UserSerializer(request.user)
    branding = ThemeSerializer(agency.branding)
    theme = ThemeSerializer(agency.theme)

    if agency.region:
        for region in agency.region.all():
            if region.boundaries:
                region_boundaries_coord = []
                region_boundaries_list = eval(region.boundaries)
                for coord in region_boundaries_list:
                    lat, long = coord.split(',')
                    region_boundaries_coord.append((lat, long))
                multi_region_boundaries.append(list(region_boundaries_coord))

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
                               "user": user.data,
                               "branding": branding.data,
                              "theme": theme.data},
                              context_instance=RequestContext(request))
