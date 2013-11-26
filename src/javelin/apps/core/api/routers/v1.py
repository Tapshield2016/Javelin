from rest_framework import routers

from core.api.viewsets.v1 import (UserViewSet, GroupViewSet, AgencyViewSet,
                                  AlertViewSet, AlertLocationViewSet,
                                  ChatMessageViewSet, MassAlertViewSet,
                                  UserProfileViewSet)


router_v1 = routers.DefaultRouter()
router_v1.register(r'users', UserViewSet)
router_v1.register(r'groups', GroupViewSet)
router_v1.register(r'agencies', AgencyViewSet)
router_v1.register(r'alerts', AlertViewSet)
router_v1.register(r'alert-locations', AlertLocationViewSet)
router_v1.register(r'chat-messages', ChatMessageViewSet)
router_v1.register(r'mass-alerts', MassAlertViewSet)
router_v1.register(r'user-profiles', UserProfileViewSet)