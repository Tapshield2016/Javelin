# -*- coding: utf-8 -*-
from views import email_add, email_list, email_delete, \
            email_send_activation, email_activate, email_make_primary, email_check_activated
from django.conf.urls import patterns, include, url
from django.conf import settings


#add an email to a User account
urlpatterns = patterns('',
    url(
        r'^email/add/$', 
        email_add, 
        name='emailmgr_email_add'
        ),
    url(
        r'^email/send_activation/$',
        email_send_activation,
        name='emailmgr_email_send_activation'
        ),
    url(
        r'^email/activate/(?P<identifier>\w+)/$',
        email_activate,
        name='emailmgr_email_activate'
        ),
    url(
        r'^email/make_primary/$',
        email_make_primary,
        name='emailmgr_email_make_primary'
        ),
    url(
        r'^email/delete/$',
        email_delete,
        name='emailmgr_email_delete'
        ),
    url(
        r'^email/$',
        email_list,
        name='emailmgr_email_list'
        ),
    url(
        r'^email/check_activated/$',
        email_check_activated,
        name='emailmgr_email_check_activated'
        ),
)
