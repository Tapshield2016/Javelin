from django.conf.urls import patterns, include, url

from routers.v1 import router_v1


urlpatterns = patterns('',
    url(r'^register/$', 'core.views.register_user'),
    url(r'^resend-verification/$', 'core.views.resend_verification_email'),
    url(r'^v1/', include(router_v1.urls)),
)
