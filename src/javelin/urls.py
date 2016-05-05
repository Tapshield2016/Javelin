from django.conf import settings
from django.conf.urls import include, url
from django.views.static import serve
from filebrowser.sites import site

from rest_framework.authtoken.views import obtain_auth_token
from rest_framework import urls as rest_framework_urls
from rest_framework_swagger import urls as rest_framework_swagger_urls
from allauth import urls as allauth_urls

from core import urls as core_urls
from shieldcommand import urls as shieldcommand_urls

# from grappelli import urls as grappelli_urls
from registration.backends.default import urls as registration_urls

from django.contrib import admin
from django.contrib.auth import views as auth_views
admin.autodiscover()


urlpatterns = [

    # (r'^admin/filebrowser/', include(site.urls)),
    # url(r'^grappelli/', include(grappelli_urls)), # grappelli URLS

    url(r'^accounts/password/reset/$',
        auth_views.password_reset,
        {'post_reset_redirect' : '/accounts/password/reset/done/'},
        name='password_reset'),
    url(r'^accounts/password/reset/done/$',
        auth_views.password_reset_done,
        name='password_reset_done'),
    url(r'^accounts/password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        auth_views.password_reset_confirm,
        {'post_reset_redirect' : '/accounts/password/done/'},
        name='password_reset_confirm'),
    url(r'^accounts/password/done/$',
        auth_views.password_reset_complete,
        name='password_reset_complete'),
    url(r'^registration/', include(registration_urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include(rest_framework_urls,
                               namespace='rest_framework')),
    url(r'^api/retrieve-token/$',
        obtain_auth_token),
    url(r'^api/', include(core_urls)), #, namespace='api')),
    url(r'^docs/', include(rest_framework_swagger_urls)),
    url(r'^social-accounts/', include(allauth_urls)),
    url(r'^', include(shieldcommand_urls)),
]

if settings.DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,}),
]