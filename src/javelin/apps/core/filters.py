import datetime

import django_filters

from django import forms
from django.utils.encoding import force_str
 
from rest_framework import ISO_8601
from rest_framework.compat import parse_datetime
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
 
 
class IsoDateTimeField(forms.DateTimeField):
    """
    It support 'iso-8601' date format too which is out the scope of
    the ``datetime.strptime`` standard library
 
    # ISO 8601: ``http://www.w3.org/TR/NOTE-datetime``
    """
    def strptime(self, value, format):
        value = force_str(value)
        if format == ISO_8601:
            parsed = parse_datetime(value)
            if parsed is None:  # Continue with other formats if doesn't match
                try:
                    parsed = datetime.datetime.fromtimestamp(float(value))
                except ValueError:
                    raise ValueError
                finally:
                    if parsed is None:
                        raise ValueError
            return parsed
        return super(IsoDateTimeField, self).strptime(value, format)
 
 
class PreciseDateTimeField(IsoDateTimeField):
    """ Only support ISO 8601 """
    def __init__(self, *args, **kwargs):
        kwargs['input_formats'] = (ISO_8601, )
        super(PreciseDateTimeField, self).__init(*args, **kwargs)
 
 
class IsoDateTimeFilter(django_filters.DateTimeFilter):
    """ Extend ``DateTimeFilter`` to filter by ISO 8601 formated dates too"""
    field_class = IsoDateTimeField
 
 
class PreciseDateTimeFilter(django_filters.DateTimeFilter):
    """ Extend ``DateTimeFilter`` to filter only by ISO 8601 formated dates """
    field_class = PreciseDateTimeField
