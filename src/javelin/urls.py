from django.conf import settings
from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    url(r'^accounts/password/reset/$',
        'django.contrib.auth.views.password_reset', 
        {'post_reset_redirect' : '/accounts/password/reset/done/'},
        name='password_reset'),
    url(r'^accounts/password/reset/done/$',
        'django.contrib.auth.views.password_reset_done',
        name='password_reset_done'),
    url(r'^accounts/password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        'django.contrib.auth.views.password_reset_confirm', 
        {'post_reset_redirect' : '/accounts/password/done/'},
        name='password_reset_confirm'),
    url(r'^accounts/password/done/$',
        'django.contrib.auth.views.password_reset_complete',
        name='password_reset_complete'),
    url(r'^registration/', include('registration.backends.default.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(r'^api/retrieve-token/$',
        'rest_framework.authtoken.views.obtain_auth_token'),
    url(r'^api/', include('core.urls')),
    url(r'^docs/', include('rest_framework_swagger.urls')),
    (r'^social-accounts/', include('allauth.urls')),
    url(r'^', include('shieldcommand.urls')),

    (r'^grappelli/', include('grappelli.urls')), # grappelli URLS
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,}),
)
