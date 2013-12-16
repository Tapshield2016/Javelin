from django.conf.urls import patterns, include, url

from api.routers.v1 import router_v1


urlpatterns = patterns('',
    url(r'^login/$', 'core.views.login'),
    url(r'^resend-verification/$', 'core.views.resend_verification_email'),
    url(r'^register/$', 'core.views.register_user'),
    url(r'^verified/$', 'core.views.verified'),
    url(r'^twilio-call-token/$', 'core.views.twilio_call_token'),
    url(r'^dial/$', 'core.views.dial'),
    url(r'^v1/', include(router_v1.urls)),
)
