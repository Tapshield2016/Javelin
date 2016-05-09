from django.conf.urls import include, url

from api.routers.v1 import router_v1
from api.routers.v1 import urlpatterns as api_views
from api.viewsets.v1 import StaticDeviceDetail

from emailmgr import urls as emailmgr_urls
from agency.views import agency_settings_form

from staticdevice.views import static_device_form, static_alert, static_disarm, register_static_device

import views

urlpatterns = [
    url(r'^login/$', views.login),
    url(r'^resend-verification/$', views.resend_verification_email),
    url(r'^register/$', views.register_user),
    url(r'^verified/$', views.verified),

    # Twilio
    url(r'^twilio-call-token/$', views.twilio_call_token),
    url(r'^dial/$', views.dial),

    # Agency Settings
    url(r'^agency-settings/$', agency_settings_form,
        name='agency_settings'),
    url(r'^static-device-form/$', static_device_form,
        name='static_device_form'),

    # Social login
    url(r'^create-facebook-user/$', views.create_facebook_user),
    url(r'^create-twitter-user/$', views.create_twitter_user),
    url(r'^create-google-user/$', views.create_google_user),
    url(r'^create-linkedin-user/$', views.create_linkedin_user),

    # Models
    url(r'^v1/', include(router_v1.urls)),
    url(r'^v1/', include(api_views)),

    # Email manager
    url(r'^', include(emailmgr_urls)),

    # Static device
    url(r'^static-device/register/$', register_static_device),
    url(r'^static-device/alert/$', static_alert),
    url(r'^static-device/disarm/$', static_disarm),
    url(r'^static-device/(?P<uuid>\w+)/$', StaticDeviceDetail.as_view(),
        name='core_static_device_details'),

    # Alert
    url(r'^alert/active-alert/$', views.find_active_alert),
    url(r'^alert/create-alert/$', views.create_alert),

    # Entourage
    url(r'^entourage/members/$', views.set_entourage_members),
]
