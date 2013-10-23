from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from rest_framework import routers
from core.views import (UserViewSet, GroupViewSet, AgencyViewSet, AlertViewSet,
                        ChatMessageViewSet, MassAlertViewSet,
                        UserProfileViewSet)

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'agencies', AgencyViewSet)
router.register(r'alerts', AlertViewSet)
router.register(r'chat-messages', ChatMessageViewSet)
router.register(r'mass-alerts', MassAlertViewSet)
router.register(r'user-profiles', UserProfileViewSet)

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(r'^api/', include(router.urls)),
    # url(r'^$', 'javelin.views.home', name='home'),
)
