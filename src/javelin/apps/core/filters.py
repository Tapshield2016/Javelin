from rest_framework.filters import BaseFilterBackend

from exceptions import MissingAgencyQueryParameterException


class AgencyParameterFilterBackend(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        filter_meta =\
            getattr(view.serializer_class.Meta.model, 'FilterMeta', None)
        if filter_meta and filter_meta.requires_agency_parameter:
            if not any(match in filter_meta.agency_relation\
                           for match in request.QUERY_PARAMS.keys()):
                raise MissingAgencyQueryParameterException()
        return queryset
