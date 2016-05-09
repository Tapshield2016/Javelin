from django.conf import settings
from django.contrib.auth.decorators import login_required
# from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render_to_response
from django.template import RequestContext
from agency.models import Agency
from core.api.serializers.v1 import AgencySerializer

import json
from django.core.serializers.json import DjangoJSONEncoder

from django.core.exceptions import ObjectDoesNotExist

from core.api.serializers.v1 import UserSerializer, ThemeSerializer, AgencySerializer, AgencyListSerializer

from rest_framework.renderers import JSONRenderer

# from django.utils.




@login_required(login_url='shieldcommand-login')
def select_agency(request):
    agencies = request.user.agency_access

    if request.user.is_superuser:
        agencies = Agency.objects.all()

    if not agencies:
        return render_to_response(
            'shieldcommand/unauthorized.html',
            context_instance=RequestContext(request)
        )

    agencies = AgencyListSerializer(agencies, many=True, context={'request': request})

    js_data = json.dumps(agencies.data, cls=DjangoJSONEncoder)

    return render_to_response('shieldcommand/agencies.html',
                              {"agencies": js_data},
                              context_instance=RequestContext(request))


@login_required(login_url='shieldcommand-login')
def index(request, agency_id=None):
    agency = request.user.agency

    if agency_id:
        try:
            agency = Agency.objects.get(pk=int(agency_id))
        except ObjectDoesNotExist:
            pass

    if not agency:
        return render_to_response(
            'shieldcommand/unauthorized.html',
            context_instance=RequestContext(request)
        )

    if not request.user.is_superuser:
        if request.user.groups.filter(name='Dispatchers').count() == 0:
            return render_to_response('shieldcommand/unauthorized.html',
                                      context_instance=RequestContext(request))

    if not agency:
        return render_to_response('shieldcommand/unauthorized.html',
                                  context_instance=RequestContext(request))

    agency_boundaries_coords = []
    multi_region_boundaries = []
    user = UserSerializer(request.user, context={'request': request})
    branding = ThemeSerializer(agency.branding, context={'request': request})
    theme = ThemeSerializer(agency.theme, context={'request': request})

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
