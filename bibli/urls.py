from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^alexandrie/admin/', include(admin.site.urls)),
    url(r'^alexandrie/', include('alexandrie.urls', namespace='alexandrie')),
)
