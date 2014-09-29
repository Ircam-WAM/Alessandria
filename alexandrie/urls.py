from django.conf import settings
from django.conf.urls import patterns, url

from alexandrie import views

urlpatterns = patterns('',
    # http://127.0.0.1:8000/alexandrie/ => go to login view
    url(r'^%s$' %settings.LOGIN_URL[1:], 'django.contrib.auth.views.login', {'template_name': 'alexandrie/login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/alexandrie'}, name='logout'),

    url(r'^home/$', views.HomeView.as_view(), name='home'),
    url(r'^reader/$', views.ReaderView.as_view(), name='reader_add'),
    # Example : /alexandrie/reader/1/
    url(r'^reader/(?P<reader_id>\d+)/$', views.ReaderView.as_view(), name='reader_detail'),
    url(r'^reader_list/$', views.ReaderListView.as_view(), name='reader_list'),

    url(r'author/add/$', views.AuthorCreateView.as_view(), name='author_add'),
    url(r'author/(?P<pk>\d+)/$', views.AuthorUpdateView.as_view(), name='author_update'),
    #url(r'author/(?P<pk>\d+)/delete/$', AuthorDelete.as_view(), name='author_delete'),
    url(r'author/list/$', views.AuthorListView.as_view(), name='author_list')
)
