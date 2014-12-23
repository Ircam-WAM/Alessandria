# Ajax autocomplete stuff
from ajax_select import LookupChannel
from alexandrie.models import Reader, BookCopy, Author, Publisher

class ReaderLookup(LookupChannel):
    model = Reader

    def get_query(self, q, request):
        return Reader.objects.filter(disabled_on=None, last_name__icontains=q).order_by('last_name')

class BookCopyLookup(LookupChannel):
    model = BookCopy

    def get_query(self, q, request):
        return BookCopy.objects.filter(disabled_on=None, book__title__icontains=q)

class AuthorLookup(LookupChannel):
    model = Author

    def get_query(self, q, request):
        return Author.objects.filter(last_name__icontains=q)

class PublisherLookup(LookupChannel):
    model = Author

    def get_query(self, q, request):
        return Publisher.objects.filter(name__icontains=q)