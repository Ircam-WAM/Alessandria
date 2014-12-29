# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.contrib import admin
from ajax_select import urls as ajax_select_urls

urlpatterns = patterns('',
    url(r'^lookups/', include(ajax_select_urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^alexandrie/', include('alexandrie.urls', namespace='alexandrie')),
)
