from django.conf.urls import patterns, include, url

#from views import register_user
from routers.v1 import router_v1


urlpatterns = patterns('',
    url(r'^register/$', 'core.views.register_user'),
    url(r'^v1/', include(router_v1.urls)),
)
