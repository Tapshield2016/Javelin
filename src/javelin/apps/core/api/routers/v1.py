from rest_framework import routers

from core.api.viewsets.v1 import (UserViewSet, GroupViewSet, AgencyViewSet,
                                  AlertViewSet, AlertLocationViewSet,
                                  ChatMessageViewSet, MassAlertViewSet,
                                  UserProfileViewSet, SocialCrimeReportViewSet,
                                  EntourageMemberViewSet, RegionViewSet, DispatchCenterViewSet,
                                  ClosedDateViewSet, DispatcherTimesViewSet)

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
router_v1.register(r'dispatcher-times', DispatcherTimesViewSet)