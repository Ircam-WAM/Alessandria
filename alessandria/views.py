# -*- coding: utf-8 -*-
import logging
import isbnlib
import datetime
import re

from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.conf import settings

from .models import (
    UserNavigationHistory, Book, BookCopy, AppliNews, Reader, ReaderBorrow, Author, Publisher, Language
)
from .forms import (
    AuthorForm, AuthorSearchForm, PublisherForm, PublisherSearchForm, BookForm, BookSearchForm,
    BookCopyForm, BookCopyDisableForm, ReaderForm, ReaderBorrowForm, ReaderDisableForm, ReaderSearchForm
)


logger = logging.getLogger(__name__)
PAGINATION_SIZE = 15


def load_user_nav_history(request, user):
    lst = UserNavigationHistory.objects.get_list(user)
    user_nav_list = []
    for user_nav in lst:
        user_nav_list.append((user_nav.url, user_nav.title))
    request.session['user_nav_list'] = user_nav_list


def clear_user_nav_history(request):
    request.session['user_nav_list'] = None


class ProtectedView(object):
    login_url = reverse_lazy('alessandria:login')

    @classmethod
    def as_view(cls, **initkwargs):
        view = super(ProtectedView, cls).as_view(**initkwargs)
        return login_required(view, login_url=cls.login_url)


class EntityCreateView(ProtectedView, CreateView):
    def form_invalid(self, form, error_msg=_("Error when saving the record.")):
        messages.error(self.request, error_msg)
        return super(EntityCreateView, self).form_invalid(form)

    def form_valid(self, form, success_msg=_("Record successful saved.")):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.instance.created_by = self.request.user
        messages.success(self.request, success_msg)
        return super(EntityCreateView, self).form_valid(form)


class EntityUpdateView(ProtectedView, UpdateView):
    def get(self, request, **kwargs):
        ret = super(EntityUpdateView, self).get(request, kwargs)
        if not UserNavigationHistory.exist_url(request.path):
            UserNavigationHistory.add(request.path, self.object._meta.verbose_name + " : " + str(self.object),
                                      self.request.user)
            load_user_nav_history(self.request, self.request.user)
        return ret

    def form_invalid(self, form, error_msg=_("Error when saving the record.")):
        messages.error(self.request, error_msg)
        return super(EntityUpdateView, self).form_invalid(form)

    def form_valid(self, form, success_msg=_("Record successful saved.")):
        form.instance.modified_by = self.request.user
        messages.success(self.request, success_msg)
        return super(EntityUpdateView, self).form_valid(form)


class EntityListView(ProtectedView, ListView):
    object_list = None

    def _build_query(self, search_fields):
        # Abstract method
        raise NotImplementedError

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        # The method of the super class will put 'object_list' and a 'paginator' and 'page_obj' objects in the context
        # of the template
        context = super(EntityListView, self).get_context_data(**kwargs)
        cur_page_nb = context['page_obj'].number
        num_pages = context['paginator'].num_pages

        pages_window = [i for i in range(max(cur_page_nb-3, 1), min(cur_page_nb+4, num_pages + 1))]
        context['pages_window'] = pages_window
        context['window_first_page_nb'] = pages_window[0]
        context['window_last_page_nb'] = pages_window[-1]

        if self.form_class is not None:
            context['search_form'] = self.form_class()
        return context

    def get(self, request, **kwargs):
        order_field = request.GET.get('order_field')
        if request.GET.get('page') is not None or order_field is not None:
            if request.session.get('search_fields') is not None:
                # Rebuild the query upon the search terms entered by the user
                self._build_query(request.session.get('search_fields'))
            else:
                if self.object_list is None:  # Make sure the subclass didn't already create self.object_list
                    self.object_list = self.model.objects.all()
        else:
            # First time we arrive on a list page
            if self.object_list is None:  # Make sure the subclass didn't already create self.object_list
                self.object_list = self.model.objects.all()
            request.session['order_field'] = None
            request.session['search_fields'] = None
        if order_field is not None:
            # Sorting request
            if request.session.get('order_field') is not None: # A previous sorting request was done on this page
                # Check if the sorting field changed according to the last sorting request
                stored_field = (
                    request.session.get('order_field')[1:]
                    if request.session.get('order_field').startswith('-') else request.session.get('order_field')
                )
                if order_field == stored_field:
                    # Invert sort order
                    if request.session.get('order_field').startswith('-'):
                        request.session['order_field'] = request.session.get('order_field')[1:]
                    else:
                        request.session['order_field'] = '-' + request.session.get('order_field')
                else:
                    # Sorting request on a new field
                    request.session['order_field'] = order_field
            else:
                # First time sorting request for this page
                request.session['order_field'] = order_field
        if request.session.get('order_field') is not None:
            self.object_list = self.object_list.order_by(request.session.get('order_field'))

        context = self.get_context_data()
        return self.render_to_response(context)

    def post(self, request):
        self._build_query(request.POST)
        request.session['search_fields'] = request.POST
        request.session['order_field'] = None
        context = self.get_context_data()
        if self.form_class is not None:
            context['search_form'] = self.form_class(request.POST)
        return self.render_to_response(context)


class EntityDeleteView(ProtectedView, DeleteView):
    pass


class HomeView(ProtectedView, TemplateView):
    template_name = 'alessandria/index.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(HomeView, self).get_context_data(**kwargs)
        context['last_books_list'] = Book.objects.all()[:10]
        context['last_appli_news_list'] = AppliNews.objects.list()[:3]
        return context


class LogoutView(TemplateView):
    def get(self, request, **kwargs):
        logout(request)
        clear_user_nav_history(request)
        return HttpResponseRedirect(reverse('alessandria:login'))


class LoginView(TemplateView):
    template_name = 'alessandria/login.html'
    logging_error_msg = _("Login error - wrong username or password.")

    def login_error(self):
        messages.error(self.request, self.logging_error_msg)
        return HttpResponseRedirect(reverse('alessandria:login'))

    def post(self, request):
        """Gather the username and password provided by the user.
        This information is obtained from the login form.
        """
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the credentials are correct.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                load_user_nav_history(request, user)
                return HttpResponseRedirect(reverse('alessandria:home'))
            else:
                # An inactive account was used - no logging in!
                messages.error(self.request, self.logging_error_msg)
                return self.login_error()
        else:
            # Bad login details were provided. So we can't log the user in.
            return self.login_error()


class Scan(TemplateView):
    template_name = 'alessandria/scan.html'
    
    def get_context_data(self, **kwargs):
        context = super(Scan, self).get_context_data(**kwargs)
        context['QRCODE_PREFIX'] = settings.QRCODE_PREFIX
        return context


class ReaderBorrowCreateView(EntityCreateView):
    template_name = 'alessandria/reader_borrow_detail.html'
    model = Book
    form_class = ReaderBorrowForm

    def form_valid(self, form):
        return super(ReaderBorrowCreateView, self).form_valid(form)


class ReaderBorrowUpdateView(EntityUpdateView):
    template_name = 'alessandria/reader_borrow_detail.html'
    model = ReaderBorrow
    form_class = ReaderBorrowForm

    def get_object(self, queryset=None):
        b_uuid = re.sub(settings.QRCODE_PREFIX, '', self.kwargs['uuid'])    
        try:
            return ReaderBorrow.objects.get(book___uuid=b_uuid)
        except :
            raise Http404
    

    def form_valid(self, form):
        return super(ReaderBorrowUpdateView, self).form_valid(form)


class ReaderBorrowDeleteView(EntityDeleteView):
    template_name = 'alessandria/confirm_delete.html'
    model = ReaderBorrow
    success_url = reverse_lazy('alessandria:reader_borrow_list')


class ReaderBorrowListView(EntityListView):
    template_name = 'alessandria/reader_borrow_list.html'
    model = ReaderBorrow
    paginate_by = PAGINATION_SIZE
    object_list = None
    form_class = None

    def _build_query(self, search_fields):
        pass

    def get(self, request, **kwargs):
        if kwargs.get('display') == 'current':
            page_title = "Emprunts en cours"
            self.object_list = ReaderBorrow.objects.list_current()
        elif kwargs.get('display') == 'late':
            page_title = "Emprunts en retard"
            self.object_list = ReaderBorrow.objects.list_late()
        else:
            page_title = "Tous les emprunts"
            self.object_list = ReaderBorrow.objects.all()
        template_response = super(ReaderBorrowListView, self).get(request, **kwargs)
        template_response.context_data['page_title'] = page_title
        template_response.context_data['display'] = kwargs.get('display')
        return template_response


class AuthorCreateView(EntityCreateView):
    template_name = 'alessandria/author_detail.html'
    model = Author
    form_class = AuthorForm

    def get_success_url(self):
        if self.kwargs.get('redirect_to_book', None) is not None:
            # We created the author from the book page
            book_post = self.request.session['book_post_form']
            book_post['authors'].append(str(self.object.id))
            self.request.session['book_post_form'] = book_post
            return reverse('alessandria:book_add', args=['from_external_page'])
        return super().get_success_url()


class AuthorUpdateView(EntityUpdateView):
    template_name = 'alessandria/author_detail.html'
    model = Author
    form_class = AuthorForm

    def form_valid(self, form):
        return super(AuthorUpdateView, self).form_valid(form)


class AuthorDeleteView(EntityDeleteView):
    template_name = 'alessandria/confirm_delete.html'
    model = Author
    success_url = reverse_lazy('alessandria:author_list')

    def get(self, request, **kwargs):
        # This method is called before displaying the page 'template_name'
        author = Author.objects.get(id=kwargs['pk'])
        if author.book_set.count() > 0:
            messages.error(self.request, _("Unable to remove this author because it is referenced in a book."))
            return redirect('alessandria:author_update', pk=author.id)
            #return redirect(author) # Call to get_absolute_url of Author model
        return super(AuthorDeleteView, self).get(request, kwargs)


class AuthorListView(EntityListView):
    template_name = 'alessandria/author_list.html'
    model = Author
    paginate_by = PAGINATION_SIZE
    form_class = AuthorSearchForm

    def _build_query(self, search_fields):
        self.object_list = self.model.objects.search(name=search_fields['last_name'])


class PublisherCreateView(EntityCreateView):
    template_name = 'alessandria/publisher_detail.html'
    model = Publisher
    form_class = PublisherForm

    def get_success_url(self):
        if self.kwargs.get('redirect_to_book', None) is not None:
            # We created the publisher from the book page
            book_post = self.request.session['book_post_form']
            book_post['publishers'].append(str(self.object.id))
            self.request.session['book_post_form'] = book_post
            return reverse('alessandria:book_add', args=['from_external_page'])
        return super().get_success_url()


class PublisherUpdateView(EntityUpdateView):
    template_name = 'alessandria/publisher_detail.html'
    model = Publisher
    form_class = PublisherForm

    def form_valid(self, form):
        return super(PublisherUpdateView, self).form_valid(form)


class PublisherDeleteView(EntityDeleteView):
    template_name = 'alessandria/confirm_delete.html'
    model = Publisher
    success_url = reverse_lazy('alessandria:publisher_list')

    def get(self, request, **kwargs):
        # This method is called before displaying the page 'template_name'
        publisher = Publisher.objects.get(id=kwargs['pk'])
        if publisher.book_set.count() > 0:
            messages.error(self.request, _("Unable to remove this publisher because it is referenced in a book."))
            return redirect('alessandria:publisher_update', pk=publisher.id)
        return super(PublisherDeleteView, self).get(request, kwargs)


class PublisherListView(EntityListView):
    template_name = 'alessandria/publisher_list.html'
    model = Publisher
    paginate_by = PAGINATION_SIZE
    form_class = PublisherSearchForm

    def _build_query(self, search_fields):
        self.object_list = self.model.objects.search(name=search_fields['name'])


def book_list_by_publisher(request, publisher_id):
    publisher = Publisher.objects.get(pk=publisher_id)
    object_list = publisher.book_set.all()
    return render(
        request,
        'alessandria/book_list_by_publisher.html',
        {
            'object_list': object_list,
            'publisher': publisher,
        },
    )


class BookCreateView(EntityCreateView):
    template_name = 'alessandria/book_detail.html'
    model = Book
    form_class = BookForm

    def get_initial(self):
        if 'from_external_page' in self.kwargs and 'book_post_form' in self.request.session:
            # If we added an author or a publisher, we want to restore the initial form
            book_post_form = self.request.session['book_post_form']
            del self.request.session['book_post_form']
            return book_post_form
        return super().get_initial()


    def get_context_data(self, **kwargs):
        """Called after the get method"""
        # Call the base implementation first to get a context
        context = super(BookCreateView, self).get_context_data(**kwargs)
        book_form = context.get('form')
        book_form.initial['language'] = Language.get_default_language()
        return context

    def form_valid(self, form):
        super(BookCreateView, self).form_valid(form)
        book_id = self.object.id
        # Automatically propose to create the first copy of the book
        return HttpResponseRedirect(reverse('alessandria:book_list'))


def save_book_form_to_session(request, dest_url):
    """
    View called from within the book page to add either a new author or a new publisher
    """
    book_post = request.POST.copy()
    book_post['publishers'] = [item for item in book_post['publishers'].split('|') if item]
    book_post['authors'] = [item for item in book_post['authors'].split('|') if item]
    request.session['book_post_form'] = book_post
    # dest_url will either contain the url to create an author or the url to create a publisher
    return HttpResponseRedirect(reverse(dest_url, args=['redirect_to_book']))


class BookUpdateView(EntityUpdateView):
    template_name = 'alessandria/book_detail.html'
    model = Book
    form_class = BookForm

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(BookUpdateView, self).get_context_data(**kwargs)
        context['bookcopy_list'] = self.object.bookcopy_set.all()
        context['borrow_list'] = ReaderBorrow.objects.list_all_by_book(self.object.id)
        return context


class BookDeleteView(EntityDeleteView):
    template_name = 'alessandria/confirm_delete.html'
    model = Book
    success_url = reverse_lazy('alessandria:book_list')


class BookListView(EntityListView):
    template_name = 'alessandria/book_list.html'
    model = Book
    paginate_by = PAGINATION_SIZE
    form_class = BookSearchForm

    def _build_query(self, search_fields):
        self.object_list = Book.objects.search(
            isbn_nb=search_fields['isbn_nb'], title=search_fields['title'], category=search_fields['category'],
            sub_category=search_fields['sub_category'], author_name=search_fields['author_name']
        )
        self.object_list = self.object_list.filter(bookcopy__isnull=(search_fields.get('has_copy') is None))
        self.object_list = self.object_list.filter(
            bookcopy__disabled_on__isnull=(search_fields.get('took_away') is None)
        )


class BookIsbnImportView(ProtectedView, TemplateView):
    template_name = 'alessandria/book_isbn_import.html'

    def post(self, request):
        cmd = request.POST['cmd']
        if cmd == 'search_isbn':
            # Search ISBN info
            isbn_nb = request.POST['isbn_nb']
            isbn_nb = isbnlib.get_canonical_isbn(isbn_nb)
            isbn_meta = None
            if isbn_nb:
                isbn_meta = isbnlib.meta(isbn_nb)
            if isbn_meta:
                logger.debug("ISBN data: {}".format(isbn_meta))
                return self._init_isbn_import(isbn_meta, request)
            else:  # ISBN not found
                return render(
                    request,
                    self.template_name,
                    {
                        'search': True,
                    },
                )
        elif cmd == 'import_isbn':
            # After submit button to import has been pressed
            lst_authors_nb = request.POST.getlist('author_nb')
            authors_ids = []
            publisher_id = None
            for s_i in lst_authors_nb:  # Loop over all the authors of the book
                i = int(s_i)
                author_id_fieldname = 'author_id_%s' % i
                if request.POST.get(author_id_fieldname):  # The author already exists in the DB
                    authors_ids.append(Author.objects.get(id=request.POST[author_id_fieldname]).id)

            if request.POST.get('publisher_id'):  # The publisher already exists in the DB
                publisher_id = Publisher.objects.get(id=request.POST['publisher_id']).id

            # Initialize the book with the values that have been entered
            publisher_ids = [publisher_id] if publisher_id is not None else []
            book_form = BookForm(
                initial={
                    'title': request.POST.get('title'),
                    'isbn_nb': request.POST.get('isbn_nb'),
                    'publish_date': request.POST.get('publish_date'),
                    'authors': authors_ids,
                    'publishers': publisher_ids,
                    'language': Language.get_default_language(),  # TODO: Change me, use isbn_meta['Language']
                    'is_isbn_import': True
                }
            )
            book_form.fields['isbn_nb'].widget.attrs['readonly'] = True
            return render(
                request,
                'alessandria/book_detail.html',
                {
                    'form': book_form,
                },
            )

    def _init_isbn_import(self, isbn_meta, request):
        # Initialize book form from isbn meta data
        book = Book.init_from_isbn(isbn_meta)
        if book.id is not None:  # Book already exists in the DB
            return render(
                request,
                self.template_name,
                {
                    'book': book,
                    'search': True,
                },
            )

        return render(
            request,
            self.template_name,
            {
                'book': book,
                'search': True,
                'authors': Author.init_from_isbn(isbn_meta),
                'publisher': Publisher.init_from_isbn(isbn_meta),
            },
        )


class BookCopyCreateView(EntityCreateView):
    template_name = 'alessandria/bookcopy_detail.html'
    model = BookCopy

    def get_form(self, form_class=BookCopyForm):
        form = super(BookCopyCreateView, self).get_form(form_class)
        self.book = Book.objects.get(pk=self.kwargs['book_id'])
        form.instance.book = self.book
        return form

    def get_success_url(self):
        return self.book.get_absolute_url()

    def form_valid(self, form):
        return super(BookCopyCreateView, self).form_valid(form)


class BookCopyUpdateView(EntityUpdateView):
    template_name = 'alessandria/bookcopy_detail.html'
    model = BookCopy
    form_class = BookCopyForm

    def get_success_url(self):
        form = super(BookCopyUpdateView, self).get_form(self.form_class)
        return form.instance.book.get_absolute_url()

    def form_valid(self, form):
        return super(BookCopyUpdateView, self).form_valid(form)


class BookCopyDisableView(EntityUpdateView):
    template_name = 'alessandria/bookcopy_disable.html'
    model = BookCopy
    form_class = BookCopyDisableForm

    def form_valid(self, form):
        if self.object.disabled_on < self.object.registered_on:
            messages.error(self.request, _("The removing date can't be prior to the registring date."))
            return redirect('alessandria:bookcopy_disable', pk=self.object.id)
        return super(BookCopyDisableView, self).form_valid(form, _("Sample successfully removed."))

    def get_success_url(self):
        return self.object.book.get_absolute_url()


class BookCopyDeleteView(EntityDeleteView):
    template_name = 'alessandria/confirm_delete.html'
    model = BookCopy

    def get_success_url(self):
        return self.object.book.get_absolute_url()


class ReaderCreateView(EntityCreateView):
    template_name = 'alessandria/reader_detail.html'
    model = Reader
    form_class = ReaderForm


class ReaderUpdateView(EntityUpdateView):
    template_name = 'alessandria/reader_detail.html'
    model = Reader
    form_class = ReaderForm

    def form_valid(self, form):
        return super(ReaderUpdateView, self).form_valid(form)


class ReaderDisableView(EntityUpdateView):
    template_name = 'alessandria/reader_disable.html'
    model = Reader
    form_class = ReaderDisableForm

    def form_valid(self, form):
        self.object.disabled_on = datetime.datetime.now()
        return super(ReaderDisableView, self).form_valid(form, _("Reader successfully disabled."))

    def get_success_url(self):
        return self.object.get_absolute_url()


class ReaderListView(EntityListView):
    template_name = 'alessandria/reader_list.html'
    model = Reader
    paginate_by = PAGINATION_SIZE
    form_class = ReaderSearchForm

    def _build_query(self, search_fields):
        self.object_list = self.model.objects.search(last_name=search_fields['last_name'])
        self.object_list = self.object_list.filter(disabled_on__isnull=(search_fields.get('reader_enabled') is not None))
