from django.conf.urls import patterns, include, url

from api.routers.v1 import router_v1
from api.viewsets.v1 import StaticDeviceDetail


urlpatterns = patterns('',
    url(r'^login/$', 'core.views.login'),
    url(r'^resend-verification/$', 'core.views.resend_verification_email'),
    url(r'^register/$', 'core.views.register_user'),
    url(r'^verified/$', 'core.views.verified'),

    # Twilio
    url(r'^twilio-call-token/$', 'core.views.twilio_call_token'),
    url(r'^dial/$', 'core.views.dial'),

    # Agency Settings
    url(r'^agency-settings/$', 'core.views.agency_settings_form',
        name='core_agency_settings'),
    url(r'^static-device-form/$', 'core.views.static_device_form',
        name='core_static_device_form'),

    # Social login
    url(r'^create-facebook-user/$', 'core.views.create_facebook_user',),
    url(r'^create-twitter-user/$', 'core.views.create_twitter_user',),
    url(r'^create-google-user/$', 'core.views.create_google_user',),
    url(r'^create-linkedin-user/$', 'core.views.create_linkedin_user',),

    # Models
    url(r'^v1/', include(router_v1.urls)),

    # Email manager
    url(r'^', include('emailmgr.urls')),

    # Static device
    url(r'^static-device/register/$', 'core.views.register_static_device'),
    url(r'^static-device/alert/$', 'core.views.static_alert'),
    url(r'^static-device/disarm/$', 'core.views.static_disarm'),
    url(r'^static-device/(?P<uuid>\w+)/$', StaticDeviceDetail.as_view()),
)
