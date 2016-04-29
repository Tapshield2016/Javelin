from django.conf.urls import url
from django.contrib.auth.views import logout, login
from views import index

urlpatterns = [
    url(r'^login/$', login,
        {'template_name':'shieldcommand/login.html'},
        name="shieldcommand-login"),
    url(r'^logout/$', logout,
        name="shieldcommand-logout",
        kwargs={'next_page': 'shieldcommand-login'}),
    url(r'^$', index, name="shieldcommand-index"),
]
