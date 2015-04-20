# -*- coding: utf-8 -*-

from datetime import datetime as stddatetime

from django.core.urlresolvers import reverse, reverse_lazy
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, render_to_response
from django.views.generic.base import TemplateView, View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

import isbnlib

from alexandrie.models import *
from alexandrie.forms import *
from alexandrie.utils import IsbnUtils

def load_user_nav_history(request, user):
    lst = UserNavigationHistory.get_list(user)
    user_nav_list = []
    for user_nav in lst:
        user_nav_list.append((user_nav.url, user_nav.title))
    request.session['user_nav_list'] = user_nav_list

def clear_user_nav_history(request):
    request.session['user_nav_list'] = None


class ProtectedView(object):
    login_url = reverse_lazy('alexandrie:login')

    @classmethod
    def as_view(cls, **initkwargs):
        view = super(ProtectedView, cls).as_view(**initkwargs)
        return login_required(view, login_url=cls.login_url)


class EntityCreateView(ProtectedView, CreateView):
    def form_invalid(self, form, error_msg=u"Erreur lors de l'enregistrement."):
        messages.error(self.request, error_msg)
        return super(EntityCreateView, self).form_invalid(form)

    def form_valid(self, form, success_msg=u"Enregistement effectué avec succès."):
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

    def form_invalid(self, form, error_msg=u"Erreur lors de l'enregistrement."):
        messages.error(self.request, error_msg)
        return super(EntityUpdateView, self).form_invalid(form)

    def form_valid(self, form, success_msg=u"Enregistement effectué avec succès."):
        form.instance.modified_by = self.request.user
        messages.success(self.request, success_msg)
        return super(EntityUpdateView, self).form_valid(form)


class EntityListView(ProtectedView, ListView):
    def get_paginator(self, object_list):
        paginator = Paginator(object_list, 15) # Nb of items per page to show
        page = self.request.GET.get('page')
        try:
            items_paginator = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            items_paginator = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            items_paginator = paginator.page(paginator.num_pages)

        return {
            'items_paginator': items_paginator,
            'range_pages_before_and_current':
                range(
                    max(1, items_paginator.number-5),
                    items_paginator.number + 1
                ),
            'range_pages_after':
                range(
                    min(paginator.num_pages + 1, items_paginator.number + 1),
                    min(paginator.num_pages, items_paginator.number + 5 ) + 1
                ),
        }


class EntityDeleteView(ProtectedView, DeleteView):
    pass


class HomeView(ProtectedView, TemplateView):
    template_name = 'alexandrie/index.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(HomeView, self).get_context_data(**kwargs)
        context['last_books_list'] = Book.objects.all()[:10]
        context['last_appli_news_list'] = AppliNews.list()[:3]
        return context

class LogoutView(TemplateView):
    def get(self, request, **kwargs):
        logout(request)
        clear_user_nav_history(request)
        return HttpResponseRedirect(reverse('alexandrie:login'))


class LoginView(TemplateView):
    template_name = 'alexandrie/login.html'

    def login_error(self):
        messages.error(self.request, u"Erreur de connexion - nom d'utilisateur / mot de passe incorrect.")
        return HttpResponseRedirect(reverse('alexandrie:login'))

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
                return HttpResponseRedirect(reverse('alexandrie:home'))
            else:
                # An inactive account was used - no logging in!
                messages.error(self.request, u"Erreur de connexion - nom d'utilisateur / mot de passe incorrect.")
                return self.login_error()
        else:
            # Bad login details were provided. So we can't log the user in.
            return self.login_error()


class ReaderBorrowCreateView(EntityCreateView):
    template_name = 'alexandrie/reader_borrow_detail.html'
    model = ReaderBorrow
    form_class = ReaderBorrowForm
    
    def form_valid(self, form):
        return super(ReaderBorrowCreateView, self).form_valid(form)

class ReaderBorrowUpdateView(EntityUpdateView):
    template_name = 'alexandrie/reader_borrow_detail.html'
    model = ReaderBorrow
    form_class = ReaderBorrowForm

    def form_valid(self, form):
        return super(ReaderBorrowUpdateView, self).form_valid(form)

class ReaderBorrowDeleteView(EntityDeleteView):
    template_name = 'alexandrie/confirm_delete.html'
    model = ReaderBorrow
    success_url = reverse_lazy('alexandrie:reader_borrow_list')

class ReaderBorrowListView(EntityListView):
    template_name = 'alexandrie/reader_borrow_list.html'
    model = ReaderBorrow

    def get(self, request, **kwargs):
        page_title = ""

        if kwargs.get('display') == 'current':
            page_title = "Emprunts en cours"
            reader_borrow_list = ReaderBorrow.list_current()
        elif kwargs.get('display') == 'late':
            page_title = "Emprunts en retard"
            reader_borrow_list = ReaderBorrow.list_late()
        else:
            page_title = "Tous les emprunts"
            reader_borrow_list = ReaderBorrow.list_all()

        p = self.get_paginator(reader_borrow_list)
        return render_to_response(
            self.template_name, {
                'object_list_p': p['items_paginator'],
                'range_pages_before_and_current': p['range_pages_before_and_current'],
                'range_pages_after': p['range_pages_after'],
                'page_title': page_title,
            },
            context_instance=RequestContext(request),
        )


class AuthorCreateView(EntityCreateView):
    template_name = 'alexandrie/author_detail.html'
    model = Author
    form_class = AuthorForm

class AuthorUpdateView(EntityUpdateView):
    template_name = 'alexandrie/author_detail.html'
    model = Author
    form_class = AuthorForm

    def form_valid(self, form):
        return super(AuthorUpdateView, self).form_valid(form)

class AuthorDeleteView(EntityDeleteView):
    template_name = 'alexandrie/confirm_delete.html'
    model = Author
    success_url = reverse_lazy('alexandrie:author_list')

    def get(self, request, **kwargs):
        # This method is called before displaying the page 'template_name'
        author = Author.objects.get(id=kwargs['pk'])
        if author.book_set.count() > 0:
            messages.error(self.request, u"Impossible de supprimer cet auteur car il est référencé dans un livre.")
            return redirect('alexandrie:author_update', pk=author.id)
            #return redirect(author) # Call to get_absolute_url of Author model
        return super(AuthorDeleteView, self).get(request, kwargs)

class AuthorListView(EntityListView):
    template_name = 'alexandrie/author_list.html'
    model = Author

    def post(self, request):
        """Method called when a search is submitted"""
        search_form = AuthorSearchForm(request.POST)
        last_name = request.POST['last_name']
        author_list = self.model.objects.all()
        if (last_name != ''):
            author_list = author_list.filter(last_name__istartswith = last_name.upper())
        p = self.get_paginator(author_list)
        return render_to_response(
            self.template_name, {
                'object_list_p': p['items_paginator'],
                'range_pages_before_and_current': p['range_pages_before_and_current'],
                'range_pages_after': p['range_pages_after'],
                'search_form': search_form,
            },
            context_instance=RequestContext(request)
        )

    def get(self, request, **kwargs):
        """Method called when the page is accessed"""
        author_list = self.model.objects.all()
        search_form = AuthorSearchForm()
        p = self.get_paginator(author_list)
        return render_to_response(
            self.template_name, {
                'object_list_p': p['items_paginator'],
                'range_pages_before_and_current': p['range_pages_before_and_current'],
                'range_pages_after': p['range_pages_after'],
                'search_form': search_form,
            },
            context_instance=RequestContext(request)
        )


class PublisherCreateView(EntityCreateView):
    template_name = 'alexandrie/publisher_detail.html'
    model = Publisher
    form_class = PublisherForm

class PublisherUpdateView(EntityUpdateView):
    template_name = 'alexandrie/publisher_detail.html'
    model = Publisher
    form_class = PublisherForm

    def form_valid(self, form):
        return super(PublisherUpdateView, self).form_valid(form)

class PublisherDeleteView(EntityDeleteView):
    template_name = 'alexandrie/confirm_delete.html'
    model = Publisher
    success_url = reverse_lazy('alexandrie:publisher_list')

    def get(self, request, **kwargs):
        # This method is called before displaying the page 'template_name'
        publisher = Publisher.objects.get(id=kwargs['pk'])
        if publisher.book_set.count() > 0:
            messages.error(self.request, u"Impossible de supprimer cet éditeur car il est référencé dans un livre.")
            return redirect('alexandrie:publisher_update', pk=publisher.id)
        return super(PublisherDeleteView, self).get(request, kwargs)

class PublisherListView(EntityListView):
    template_name = 'alexandrie/publisher_list.html'
    model = Publisher
    context_object_name = 'publisher_list'

    def get(self, request, **kwargs):
        """Method called when the page is accessed"""
        search_form = PublisherSearchForm()
        publisher_list = self.model.objects.all()
        p = self.get_paginator(publisher_list)
        return render_to_response(
            self.template_name, {
                'object_list_p': p['items_paginator'],
                'range_pages_before_and_current': p['range_pages_before_and_current'],
                'range_pages_after': p['range_pages_after'],
                'search_form': search_form,
            },
            context_instance=RequestContext(request)
        )

    def post(self, request, **kwargs):
        """Method called when a search is submited"""
        search_form = PublisherSearchForm(request.POST)
        publisher_list = self.model.objects.all()
        name = request.POST['name']
        if name != '':
            publisher_list = publisher_list.filter(name__istartswith = name.upper())
        p = self.get_paginator(publisher_list)
        return render_to_response(
            self.template_name, {
                'object_list_p': p['items_paginator'],
                'range_pages_before_and_current': p['range_pages_before_and_current'],
                'range_pages_after': p['range_pages_after'],
                'search_form': search_form,
            },
            context_instance=RequestContext(request)
        )


class BookCreateView(EntityCreateView):
    template_name = 'alexandrie/book_detail.html'
    model = Book
    form_class = BookForm

    def get_context_data(self, **kwargs):
        # Called after the get method
        # Call the base implementation first to get a context
        context = super(BookCreateView, self).get_context_data(**kwargs)
        book_form = context.get('form')
        book_form.initial['language'] = Language.get_default_language()
        return context

    def form_valid(self, form):
        super(BookCreateView, self).form_valid(form)
        book_id = self.object.id
        # Automatically propose to create the first copy of the book
        return HttpResponseRedirect(reverse('alexandrie:bookcopy_add', args=[book_id]))

class BookUpdateView(EntityUpdateView):
    template_name = 'alexandrie/book_detail.html'
    model = Book
    form_class = BookForm

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(BookUpdateView, self).get_context_data(**kwargs)
        context['bookcopy_list'] = self.object.bookcopy_set.all()
        context['borrow_list'] = ReaderBorrow.list_all_by_book(self.object.id)
        return context

class BookDeleteView(EntityDeleteView):
    template_name = 'alexandrie/confirm_delete.html'
    model = Book
    success_url = reverse_lazy('alexandrie:book_list')

class BookListView(EntityListView):
    template_name = 'alexandrie/book_list.html'
    model = Book

    def post(self, request):
        """Method called when a search is submitted"""
        search_form = BookSearchForm(request.POST)
        title = request.POST['title']
        category = request.POST['category']
        sub_category = request.POST['sub_category']
        isbn_nb = request.POST['isbn_nb']
        book_list = self.model.objects.all()
        if (isbn_nb != ''):
            isbn_nb = isbnlib.get_canonical_isbn(isbn_nb)
            book_list = book_list.filter(isbn_nb = isbn_nb)
        if (title != ''):
            book_list = book_list.filter(title__icontains = title)
        if (category != ''):
            book_list = book_list.filter(category__id = category)
        if (sub_category != ''):
            book_list = book_list.filter(sub_category__id = sub_category)

        p = self.get_paginator(book_list)

        return render_to_response(
            self.template_name, {
                'object_list_p': p['items_paginator'],
                'range_pages_before_and_current': p['range_pages_before_and_current'],
                'range_pages_after': p['range_pages_after'],
                'search_form': search_form,
            },
            context_instance=RequestContext(request)
        )

    def get(self, request, **kwargs):
        """Method called when the page is accessed"""
        book_list = self.model.objects.all()
        p = self.get_paginator(book_list)
        search_form = BookSearchForm()
        return render_to_response(
            self.template_name, {
                'object_list_p': p['items_paginator'],
                'range_pages_before_and_current': p['range_pages_before_and_current'],
                'range_pages_after': p['range_pages_after'],
                'search_form': search_form,
            },
            context_instance=RequestContext(request)
        )


class BookIsbnImportView(ProtectedView, TemplateView):
    template_name = 'alexandrie/book_isbn_import.html'

    def post(self, request):
        cmd = request.POST['cmd']
        if cmd == 'search_isbn':
            book = None
            authors_form = None
            publisher_form = None
            book_form = None
            # Search ISBN info
            isbn_nb = request.POST['isbn_nb']
            isbn_nb = isbnlib.get_canonical_isbn(isbn_nb)
            isbn_meta = None
            if isbn_nb:
                isbn_meta = isbnlib.meta(isbn_nb)
            if isbn_meta:
                isbn_meta_nb = IsbnUtils.get_isbn_nb_from_meta(isbn_meta)
                #if isbn_meta_nb == isbn_nb: # Just to make sure there is no bug in isbn lib
                book = Book.init_from_isbn(isbn_meta)
                book_form = BookForm(instance=book)
                if book_form.instance.id:
                    return render_to_response(
                        self.template_name, {
                            'book_form': book_form,
                            'search': True,
                        },
                        context_instance=RequestContext(request)
                    )
                country_code = IsbnUtils.get_country_code(isbn_meta)
                authors_form = []
                i=0
                authors = Author.init_from_isbn(isbn_meta)
                for author in authors:
                    author_form = self._create_author_form(prefix='author_create_%s' %i, instance=author)
                    authors_form.append(author_form)
                    i+=1

                publisher = Publisher.init_from_isbn(isbn_meta)
                publisher_form = self._create_publisher_form(instance=publisher)

                return render_to_response(
                    self.template_name, {
                        'book_form': book_form,
                        'search': True,
                        'authors_form': authors_form,
                        'publisher_form': publisher_form,
                    },
                    context_instance=RequestContext(request)
                )
            else:
                return render_to_response(
                    self.template_name, {
                        'search': True,
                    },
                    context_instance=RequestContext(request)
                )
        elif cmd == 'import_isbn':
            # After submit button to import has been pressed
            lst_authors_nb = request.POST.getlist('author_nb')
            authors_form = []
            authors_ids = []
            publisher_id = None
            publisher_form = None
            is_error_in_form = False
            for s_i in lst_authors_nb: # Loop over all the authors of the book
                i = int(s_i)
                author_id_fieldname = 'author_id_%s' % i
                if not request.POST.get(author_id_fieldname): # The author doesn't exist in the DB
                    if request.POST.get('author_to_create_%s' % i): # It is checked to be created
                        author_form = self._create_author_form(form_post=request.POST, prefix='author_create_%s' %i)
                        if not is_error_in_form:
                            is_error_in_form = not author_form.is_valid()
                        authors_form.append(author_form)
                else: # The author already exists in the DB
                    authors_ids.append(Author.objects.get(id=request.POST[author_id_fieldname]).id)

            if not request.POST.get('publisher_id'): # The publisher doesn't exist in the db
                if request.POST.get('publisher_to_create'): # The publisher was checked to be created
                    publisher_form = self._create_publisher_form(form_post=request.POST)
                    if not is_error_in_form:
                        is_error_in_form = not publisher_form.is_valid()
            else: # The publisher already exists in the DB
                publisher_id = Publisher.objects.get(id=request.POST['publisher_id']).id

            if not is_error_in_form:
                # Create the authors in the DB from the page form
                for author_form in authors_form:
                    author_form.instance.created_by = request.user
                    author_form.instance.is_isbn_import = True
                    author_form.save()
                    authors_ids.append(author_form.instance.id)
                if publisher_form:
                    # Create the publisher in the DB from the page form
                    publisher_form.instance.created_by = request.user
                    publisher_form.instance.is_isbn_import = True
                    publisher_form.save()
                    publisher_id = publisher_form.instance.id
                # Initialize the book with the values that have been entered
                book_form = BookForm(
                    initial={
                        'title': request.POST.get('title'),
                        'isbn_nb': request.POST.get('isbn_nb'),
                        'publish_date': request.POST.get('publish_date'),
                        'authors': authors_ids,
                        'publishers': [publisher_id],
                        'language': Language.get_default_language(), # TODO: Change me, use isbn_meta['Language']
                        'is_isbn_import': True
                    }
                )
                book_form.fields['isbn_nb'].widget.attrs['readonly'] = True
                return render_to_response(
                    'alexandrie/book_detail.html', {
                        'form': book_form,
                    },
                    context_instance=RequestContext(request)
                )
            else: # Error in one of the forms => display the import page again
                return render_to_response(
                    self.template_name, {
                        'book_form': book_form,
                        'authors_form': authors_form,
                        'publisher_form': publisher_form,
                    },
                    context_instance=RequestContext(request)
                )

    def _create_author_form(self, prefix, instance=None, form_post=None):
        author_form = None
        if instance:
            author_form = AuthorForm(prefix=prefix, instance=instance)
        if form_post:
            author_form = AuthorForm(form_post, prefix=prefix)
        # Remove useless fields
        author_form.fields.pop(key='notes')
        author_form.fields.pop(key='website')
        return author_form

    def _create_publisher_form(self, instance=None, form_post=None):
        publisher_form = None
        if instance:
            publisher_form = PublisherForm(instance=instance)
        if form_post:
            publisher_form = PublisherForm(form_post)
        # Remove useless fields
        publisher_form.fields.pop(key='notes')
        return publisher_form


class BookCopyCreateView(EntityCreateView):
    template_name = 'alexandrie/bookcopy_detail.html'
    model = BookCopy
    form_class = BookCopyForm

    def get_form(self, form_class):
        form = super(BookCopyCreateView, self).get_form(form_class)
        self.book = Book.objects.get(pk=self.kwargs['book_id'])
        form.instance.book = self.book
        return form

    def get_success_url(self):
        return self.book.get_absolute_url()

    def form_valid(self, form):
        return super(BookCopyCreateView, self).form_valid(form)

class BookCopyUpdateView(EntityUpdateView):
    template_name = 'alexandrie/bookcopy_detail.html'
    model = BookCopy
    form_class = BookCopyForm

    def get_success_url(self):
        form = super(BookCopyUpdateView, self).get_form(self.form_class)
        return form.instance.book.get_absolute_url()

    def form_valid(self, form):
        return super(BookCopyUpdateView, self).form_valid(form)

class BookCopyDisableView(EntityUpdateView):
    template_name = 'alexandrie/bookcopy_disable.html'
    model = BookCopy
    form_class = BookCopyDisableForm

    def form_valid(self, form):
        if self.object.disabled_on < self.object.registered_on:
            messages.error(self.request, u"La date de retrait ne peut etre antérieure à la date d'enregistrement.")
            return redirect('alexandrie:bookcopy_disable', pk=self.object.id)
        return super(BookCopyDisableView, self).form_valid(form, u"L'exemplaire a été retiré avec succès.")

    def get_success_url(self):
        return self.object.book.get_absolute_url()

class BookCopyDeleteView(EntityDeleteView):
    template_name = 'alexandrie/confirm_delete.html'
    model = BookCopy

    def get_success_url(self):
        return self.object.book.get_absolute_url()


class ReaderCreateView(EntityCreateView):
    template_name = 'alexandrie/reader_detail.html'
    model = Reader
    form_class = ReaderForm

class ReaderUpdateView(EntityUpdateView):
    template_name = 'alexandrie/reader_detail.html'
    model = Reader
    form_class = ReaderForm

    def form_valid(self, form):
        return super(ReaderUpdateView, self).form_valid(form)

class ReaderDisableView(EntityUpdateView):
    template_name = 'alexandrie/reader_disable.html'
    model = Reader
    form_class = ReaderDisableForm

    def form_valid(self, form):
        self.object.disabled_on = stddatetime.now()
        return super(ReaderDisableView, self).form_valid(form, u"Le lecteur a été désactivé avec succès.")

    def get_success_url(self):
        return self.object.get_absolute_url()

class ReaderListView(EntityListView):
    template_name = 'alexandrie/reader_list.html'
    model = Reader

    def post(self, request):
        """Method called when a search is submitted"""
        search_form = ReaderSearchForm(request.POST)
        last_name = request.POST['last_name']
        reader_list = self.model.objects.all()
        if (last_name != ''):
            reader_list = reader_list.filter(last_name__istartswith = last_name.upper())

        p = self.get_paginator(reader_list)

        return render_to_response(
            self.template_name, {
                'object_list_p': p['items_paginator'],
                'range_pages_before_and_current': p['range_pages_before_and_current'],
                'range_pages_after': p['range_pages_after'],
                'search_form': search_form,
            },
            context_instance=RequestContext(request)
        )

    def get(self, request, **kwargs):
        """Method called when the page is accessed"""
        reader_list = self.model.objects.all()
        search_form = ReaderSearchForm()
        p = self.get_paginator(reader_list)
        return render_to_response(
            self.template_name, {
                'object_list_p': p['items_paginator'],
                'range_pages_before_and_current': p['range_pages_before_and_current'],
                'range_pages_after': p['range_pages_after'],
                'search_form': search_form,
            },
            context_instance=RequestContext(request)
        )