from django.conf import settings
from django.conf.urls import patterns, url

from alexandrie import views

urlpatterns = patterns('',
    # http://127.0.0.1:8000/alexandrie/ => go to login view
    url(r'^%s$' %settings.LOGIN_URL[1:], 'django.contrib.auth.views.login', {'template_name': 'alexandrie/login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/alexandrie'}, name='logout'),

    url(r'^home/$', views.HomeView.as_view(), name='home'),

    url(r'reader/add/$', views.ReaderCreateView.as_view(), name='reader_add'),
    url(r'reader/(?P<pk>\d+)/$', views.ReaderUpdateView.as_view(), name='reader_update'),
    url(r'reader/list/$', views.ReaderListView.as_view(), name='reader_list'),
    url(r'reader/(?P<pk>\d+)/disable/$', views.ReaderDisableView.as_view(), name='reader_disable'),

    url(r'author/add/$', views.AuthorCreateView.as_view(), name='author_add'),
    url(r'author/(?P<pk>\d+)/$', views.AuthorUpdateView.as_view(), name='author_update'),
    url(r'author/(?P<pk>\d+)/delete/$', views.AuthorDeleteView.as_view(), name='author_delete'),
    url(r'author/list/$', views.AuthorListView.as_view(), name='author_list'),

    url(r'book/add/$', views.BookCreateView.as_view(), name='book_add'),
    url(r'book/(?P<pk>\d+)/$', views.BookUpdateView.as_view(), name='book_update'),
    url(r'book/(?P<pk>\d+)/delete/$', views.BookDeleteView.as_view(), name='book_delete'),
    url(r'book/list/$', views.BookListView.as_view(), name='book_list'),

    url(r'bookcopy/add/(?P<book_id>\d+)/$', views.BookCopyCreateView.as_view(), name='bookcopy_add'),
    url(r'bookcopy/(?P<pk>\d+)/$', views.BookCopyUpdateView.as_view(), name='bookcopy_update'),
    url(r'bookcopy/(?P<pk>\d+)/disable/$', views.BookCopyDisableView.as_view(), name='bookcopy_disable'),
    url(r'bookcopy/(?P<pk>\d+)/delete/$', views.BookCopyDeleteView.as_view(), name='bookcopy_delete'),
)
