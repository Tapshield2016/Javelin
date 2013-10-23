from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from core.routers.v1 import router_v1


urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(r'^api/v1/', include(router_v1.urls)),
)
