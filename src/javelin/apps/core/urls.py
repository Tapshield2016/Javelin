from django.conf.urls import patterns, include, url

from api.routers.v1 import router_v1


urlpatterns = patterns('',
    url(r'^login/$', 'core.views.login'),
    url(r'^resend-verification/$', 'core.views.resend_verification_email'),
    url(r'^register/$', 'core.views.register_user'),
    url(r'^verified/$', 'core.views.verified'),
    url(r'^twilio-call-token/$', 'core.views.twilio_call_token'),
    url(r'^dial/$', 'core.views.dial'),
    url(r'^agency-settings/$', 'core.views.agency_settings_form',
        name='core_agency_settings'),
    url(r'^create-facebook-user/$', 'core.views.create_facebook_user',),
    url(r'^create-twitter-user/$', 'core.views.create_twitter_user',),
    url(r'^create-google-user/$', 'core.views.create_google_user',),
    url(r'^create-linkedin-user/$', 'core.views.create_linkedin_user',),
    url(r'^v1/', include(router_v1.urls)),
    url(r'^email/', include('emailmgr.urls')),
)
