# -*- coding: utf-8 -*-
"""
Ajax autocomplete stuff
"""

from django.db.models import Q

from ajax_select import LookupChannel, register
from alessandria.models import Reader, BookCopy, Author, Publisher

@register('reader_list')
class ReaderLookup(LookupChannel):
    model = Reader

    def get_query(self, q, request):
        return Reader.objects.filter(
            Q(last_name__icontains=q.upper()) | Q(first_name__icontains=q.title())
        ).filter(
            disabled_on=None
        ).order_by('last_name')

@register('bookcopy_list')
class BookCopyLookup(LookupChannel):
    model = BookCopy

    def get_query(self, q, request):
        return BookCopy.objects.filter(disabled_on=None, book__title__icontains=q.capitalize())

@register('author_list')
class AuthorLookup(LookupChannel):
    model = Author

    def get_query(self, q, request):
        return Author.objects.filter(
            Q(last_name__icontains=q.upper()) | Q(first_name__icontains=q.title()) | Q(alias__icontains=q.title())
        ).order_by('last_name')

@register('publisher_list')
class PublisherLookup(LookupChannel):
    model = Publisher

    def get_query(self, q, request):
        return Publisher.objects.filter(name__icontains=q.upper())
