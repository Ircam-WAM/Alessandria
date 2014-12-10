from datetime import datetime as stddatetime

from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.forms.models import inlineformset_factory
from django.views.generic.base import TemplateView, View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from nested_formset import nestedformset_factory

from ajax_select import LookupChannel

from alexandrie.models import *
from alexandrie.forms import *


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
    pass

class EntityDeleteView(ProtectedView, DeleteView):
    pass


class HomeView(TemplateView):
    template_name = 'alexandrie/index.html'


class LogoutView(TemplateView):
    def get(self, request, **kwargs):
        logout(request)
        clear_user_nav_history(request)
        return HttpResponseRedirect(reverse('alexandrie:login'))


class LoginView(TemplateView):
    template_name = 'alexandrie/login.html'

    def login_error(self):
        messages.error(self.request, u"Erreur de connexion - nom d'utilisateur / mot de passe incorrect.")
        return render_to_response(
            self.template_name, context_instance=RequestContext(request)
        )

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
            messages.error(self.request, u"Erreur de connexion - nom d'utilisateur / mot de passe incorrect.")
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
        if kwargs['display'] == 'all':
            page_title = "Tous les emprunts"
            reader_borrow_list = ReaderBorrow.list_all()
        elif kwargs['display'] == 'current':
            page_title = "Emprunts en cours"
            reader_borrow_list = ReaderBorrow.list_current()
        elif kwargs['display'] == 'late':
            page_title = "Emprunts en retard"
            reader_borrow_list = ReaderBorrow.list_late()
        return render_to_response(self.template_name,
                                  {
                                    'reader_borrow_list': reader_borrow_list,
                                    'page_title': page_title,
                                  },
                                  context_instance=RequestContext(request),
        )


class AuthorCreateView(EntityCreateView):
    template_name = 'alexandrie/author_detail.html'
    model = Author
    form_class = AuthorForm
    
    def form_valid(self, form):
        form.instance.last_name = form.instance.last_name.upper()
        form.instance.first_name = form.instance.first_name.capitalize()
        return super(AuthorCreateView, self).form_valid(form)

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
            author_list = author_list.filter(last_name__istartswith = last_name)
        return render_to_response(
            self.template_name, {
                'author_list': author_list,
                'search_form': search_form,
            },
            context_instance=RequestContext(request)
        )

    def get(self, request, **kwargs):
        """Method called when the page is accessed"""
        author_list = self.model.objects.all()
        search_form = AuthorSearchForm()
        return render_to_response(
            self.template_name, {
                'author_list': author_list,
                'search_form': search_form,
            },
            context_instance=RequestContext(request)
        )


class PublisherCreateView(EntityCreateView):
    template_name = 'alexandrie/publisher_detail.html'
    model = Publisher
    form_class = PublisherForm
    
    def form_valid(self, form):
        form.instance.name = form.instance.name.upper()
        return super(PublisherCreateView, self).form_valid(form)

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


class BookCreateView(EntityCreateView):
    template_name = 'alexandrie/book_detail.html'
    model = Book
    form_class = BookForm
    
    def form_valid(self, form):
        return super(BookCreateView, self).form_valid(form)

class BookUpdateView(EntityUpdateView):
    template_name = 'alexandrie/book_detail.html'
    model = Book
    form_class = BookForm

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(BookUpdateView, self).get_context_data(**kwargs)
        context['bookcopy_list'] = self.object.bookcopy_set.all()
        return context

    def form_valid(self, form):
        return super(BookUpdateView, self).form_valid(form)

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
        book_list = self.model.objects.all()
        if (title != ''):
            book_list = book_list.filter(title__icontains = title)
        if (category != ''):
            book_list = book_list.filter(category__id = category)
        if (sub_category != ''):
            book_list = book_list.filter(sub_category__id = sub_category)
        return render_to_response(
            self.template_name, {
                'book_list': book_list,
                'search_form': search_form,
            },
            context_instance=RequestContext(request)
        )

    def get(self, request, **kwargs):
        """Method called when the page is accessed"""
        book_list = self.model.objects.all()
        search_form = BookSearchForm()
        return render_to_response(
            self.template_name, {
                'book_list': book_list,
                'search_form': search_form,
            },
            context_instance=RequestContext(request)
        )


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
    
    def form_valid(self, form):
        form.instance.last_name = form.instance.last_name.upper()
        form.instance.first_name = form.instance.first_name.capitalize()
        return super(ReaderCreateView, self).form_valid(form)

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
            reader_list = reader_list.filter(last_name__istartswith = last_name)
        return render_to_response(
            self.template_name, {
                'reader_list': reader_list,
                'search_form': search_form,
            },
            context_instance=RequestContext(request)
        )

    def get(self, request, **kwargs):
        """Method called when the page is accessed"""
        reader_list = self.model.objects.all()
        search_form = ReaderSearchForm()
        return render_to_response(
            self.template_name, {
                'reader_list': reader_list,
                'search_form': search_form,
            },
            context_instance=RequestContext(request)
        )

# Ajax autocomplete stuff

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