# -*- coding: utf-8 -*-

from django.conf.urls import url

from alessandria import views
from alessandria import ajax
from django.conf import settings

urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),

    url(r'reader_borrow/add/$', views.ReaderBorrowCreateView.as_view(), name='reader_borrow_add'),
    url(r'reader_borrow/(?P<uuid>' + settings.QRCODE_PREFIX + settings.QRCODE_SEP + '[a-z0-9]{5})/$', views.ReaderBorrowUpdateView.as_view(), name='reader_borrow_update'),

    url(r'reader_borrow/list/$', views.ReaderBorrowListView.as_view(), name='reader_borrow_list'),
    url(r'reader_borrow/list/(?P<display>\w+)/$', views.ReaderBorrowListView.as_view(), name='reader_borrow_list'),
    url(r'reader_borrow/(?P<pk>\d+)/delete/$', views.ReaderBorrowDeleteView.as_view(), name='reader_borrow_delete'),

    url(r'reader/add/$', views.ReaderCreateView.as_view(), name='reader_add'),
    url(r'reader/(?P<pk>\d+)/$', views.ReaderUpdateView.as_view(), name='reader_update'),
    url(r'reader/list/$', views.ReaderListView.as_view(), name='reader_list'),
    url(r'reader/(?P<pk>\d+)/disable/$', views.ReaderDisableView.as_view(), name='reader_disable'),

    url(r'author/add/(?P<redirect_to_book>\w+)?$', views.AuthorCreateView.as_view(), name='author_add'),
    url(r'author/(?P<pk>\d+)/$', views.AuthorUpdateView.as_view(), name='author_update'),
    url(r'author/(?P<pk>\d+)/delete/$', views.AuthorDeleteView.as_view(), name='author_delete'),
    url(r'author/list/$', views.AuthorListView.as_view(), name='author_list'),

    url(r'publisher/add/(?P<redirect_to_book>\w+)?$', views.PublisherCreateView.as_view(), name='publisher_add'),
    url(r'publisher/(?P<pk>\d+)/$', views.PublisherUpdateView.as_view(), name='publisher_update'),
    url(r'publisher/(?P<pk>\d+)/delete/$', views.PublisherDeleteView.as_view(), name='publisher_delete'),
    url(r'publisher/list/$', views.PublisherListView.as_view(), name='publisher_list'),
    url(r'publisher/(?P<publisher_id>\d+)/books/$', views.book_list_by_publisher, name='book_list_by_publisher'),

    url(r'book/add/(?P<from_external_page>\w+)?$', views.BookCreateView.as_view(), name='book_add'),
    url(r'^book/(?P<pk>\d+|' + settings.QRCODE_PREFIX + settings.QRCODE_SEP + '[a-z0-9]{5})/$', views.BookUpdateView.as_view(), name='book_update'),
    url(r'book/(?P<pk>\d+)/delete/$', views.BookDeleteView.as_view(), name='book_delete'),
    url(r'book/list/$', views.BookListView.as_view(), name='book_list'),
    url(r'book/save_book_form_to_session/(?P<dest_url>\S+)/$', views.save_book_form_to_session, name='save_book_form_to_session'),

    url(r'book/isbn/import/$', views.BookIsbnImportView.as_view(), name='book_isbn_import'),

    url(r'bookcopy/add/(?P<book_id>\d+)/$', views.BookCopyCreateView.as_view(), name='bookcopy_add'),
    url(r'bookcopy/(?P<pk>\d+)/$', views.BookCopyUpdateView.as_view(), name='bookcopy_update'),
    url(r'bookcopy/(?P<pk>\d+)/disable/$', views.BookCopyDisableView.as_view(), name='bookcopy_disable'),
    url(r'bookcopy/(?P<pk>\d+)/delete/$', views.BookCopyDeleteView.as_view(), name='bookcopy_delete'),

    url(r'ajax/get/book_sub_categories/?$', ajax.get_book_sub_categories, name='get_book_sub_categories'),

# AJOUT D'UN ONGLET...
    url(r'scan/$', views.Scan.as_view(), name='matScan'),
]
