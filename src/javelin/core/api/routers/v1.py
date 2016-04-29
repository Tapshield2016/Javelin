from rest_framework import routers
from django.conf.urls import patterns, include, url

from core.api.viewsets.v1 import (UserViewSet, GroupViewSet, AgencyViewSet,
                                  AlertViewSet, AlertLocationViewSet, ThemeViewSet,
                                  ChatMessageViewSet, MassAlertViewSet,
                                  UserProfileViewSet, SocialCrimeReportViewSet,
                                  EntourageMemberViewSet, RegionViewSet, DispatchCenterViewSet,
                                  ClosedDateViewSet, PeriodViewSet, StaticDeviceViewSet,
                                  EntourageSessionViewSet, TrackingLocationViewSet, NamedLocationViewSet,
                                  UserNotificationViewSet)


router_v1 = routers.DefaultRouter()
router_v1.register(r'users', UserViewSet)
router_v1.register(r'groups', GroupViewSet)
router_v1.register(r'agencies', AgencyViewSet)
router_v1.register(r'alerts', AlertViewSet)
router_v1.register(r'alert-locations', AlertLocationViewSet)
router_v1.register(r'chat-messages', ChatMessageViewSet)
router_v1.register(r'mass-alerts', MassAlertViewSet)
router_v1.register(r'user-profiles', UserProfileViewSet)
router_v1.register(r'social-crime-reports', SocialCrimeReportViewSet)
router_v1.register(r'entourage-members', EntourageMemberViewSet)
router_v1.register(r'region', RegionViewSet)
router_v1.register(r'dispatch-center', DispatchCenterViewSet)
router_v1.register(r'closed-date', ClosedDateViewSet)
router_v1.register(r'opening-hours', PeriodViewSet)
router_v1.register(r'static-device', StaticDeviceViewSet)
router_v1.register(r'theme', ThemeViewSet)
router_v1.register(r'entourage-sessions', EntourageSessionViewSet)
router_v1.register(r'tracking-locations', TrackingLocationViewSet)
router_v1.register(r'named-locations', NamedLocationViewSet)
router_v1.register(r'user-notifications', UserNotificationViewSet)
