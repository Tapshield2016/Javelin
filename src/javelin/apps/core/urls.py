from django.conf.urls import patterns, include, url

from api.routers.v1 import router_v1


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

    # social login
    url(r'^create-facebook-user/$', 'core.views.create_facebook_user',),
    url(r'^create-twitter-user/$', 'core.views.create_twitter_user',),
    url(r'^create-google-user/$', 'core.views.create_google_user',),
    url(r'^create-linkedin-user/$', 'core.views.create_linkedin_user',),

    # models
    url(r'^v1/', include(router_v1.urls)),

    # email manager
    url(r'^', include('emailmgr.urls')),

    # Talkaphone
    url(r'^register-talkaphone-device/$', 'core.views.register_talkaphone_device'),
    url(r'^talkaphone-alert/$', 'core.views.talkaphone_alert'),
    url(r'^talkaphone-disarm/$', 'core.views.talkaphone_disarm'),
)
