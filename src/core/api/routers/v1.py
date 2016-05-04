from rest_framework import routers
from django.conf.urls import url

from core.api.viewsets.v1 import (UserViewSet, GroupViewSet, AgencyViewSet,
                                  AlertViewSet, AlertLocationViewSet, ThemeViewSet,
                                  ChatMessageViewSet, MassAlertViewSet,
                                  UserProfileViewSet, SocialCrimeReportViewSet,
                                  EntourageMemberViewSet, RegionViewSet, DispatchCenterViewSet,
                                  ClosedDateViewSet, PeriodViewSet, StaticDeviceViewSet,
                                  EntourageSessionViewSet, TrackingLocationViewSet, NamedLocationViewSet,
                                  UserNotificationViewSet)

router_v1 = routers.DefaultRouter()
router_v1.register(r'users', UserViewSet, base_name="User")
router_v1.register(r'groups', GroupViewSet)
router_v1.register(r'agencies', AgencyViewSet, base_name="Agency")
router_v1.register(r'alerts', AlertViewSet)
router_v1.register(r'alert-locations', AlertLocationViewSet)
router_v1.register(r'chat-messages', ChatMessageViewSet)
router_v1.register(r'mass-alerts', MassAlertViewSet)
router_v1.register(r'user-profiles', UserProfileViewSet)
router_v1.register(r'social-crime-reports', SocialCrimeReportViewSet, base_name="SocialCrimeReport")
router_v1.register(r'entourage-members', EntourageMemberViewSet, base_name="EntourageMember")
router_v1.register(r'region', RegionViewSet)
router_v1.register(r'dispatch-center', DispatchCenterViewSet)
router_v1.register(r'closed-date', ClosedDateViewSet)
router_v1.register(r'opening-hours', PeriodViewSet)
router_v1.register(r'static-device', StaticDeviceViewSet)
router_v1.register(r'theme', ThemeViewSet)
router_v1.register(r'entourage-sessions', EntourageSessionViewSet)
router_v1.register(r'tracking-locations', TrackingLocationViewSet)
router_v1.register(r'named-locations', NamedLocationViewSet)
router_v1.register(r'user-notifications', UserNotificationViewSet, base_name="UserNotification")

user_detail = UserViewSet.as_view({
    'get': 'retrieve'
})
agency_detail = AgencyViewSet.as_view({
    'get': 'retrieve'
})
social_crime_detail = SocialCrimeReportViewSet.as_view({
    'get': 'retrieve'
})
entourage_member_detail = EntourageMemberViewSet.as_view({
    'get': 'retrieve'
})
user_note_detail = UserNotificationViewSet.as_view({
    'get': 'retrieve'
})

urls = [
    url(r'^users/(?P<pk>[0-9]+)/$', user_detail, name='agencyuser-detail'),
    url(r'^agencies/(?P<pk>[0-9]+)/$', agency_detail, name='agency-detail'),
    url(r'^social-crime-reports/(?P<pk>[0-9]+)/$', social_crime_detail, name='socialcrimereport-detail'),
    url(r'^entourage-members/(?P<pk>[0-9]+)/$', entourage_member_detail, name='entouragemember-detail'),
    url(r'^user-notifications/(?P<pk>[0-9]+)/$', user_note_detail, name='usernotification-detail'),
]
