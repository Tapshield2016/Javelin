from django.conf.urls import patterns, include, url

from shieldcommand.views import index

urlpatterns = patterns('',
    url(r'^login/$', 'django.contrib.auth.views.login',
        {'template_name':'shieldcommand/login.html'},
        name="shieldcommand-login"),
    url(r'^logout/$', 'django.contrib.auth.views.logout',
        name="shieldcommand-logout",
        kwargs={'next_page': 'shieldcommand-login'}),
    url(r'^$', index, name="shieldcommand-index"),
)
