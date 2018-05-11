# -*- coding: utf-8 -*-
"""
Ajax autocomplete stuff
"""

from django.db.models import Q

from ajax_select import LookupChannel, register
from alessandria.models import Reader, BookCopy, Author, Publisher, Book

@register('reader_list')
class ReaderLookup(LookupChannel):
    model = Reader
    
    def get_query(self, q, request):
        return Reader.objects.filter(
            Q(last_name__icontains=q.upper()) | Q(first_name__icontains=q.title())
        ).filter(
            disabled_on=None
        ).order_by('last_name')

@register('book_list')
class BookLookup(LookupChannel):
    model = Book

    def get_query(self, q, request):
        print("q", q) 
        return Book.objects.filter(title__icontains=q)

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
