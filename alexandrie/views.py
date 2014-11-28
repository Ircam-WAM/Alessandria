from datetime import datetime as stddatetime

from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.forms.models import inlineformset_factory
from django.views.generic.base import TemplateView, View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.template import RequestContext

from nested_formset import nestedformset_factory

from alexandrie.models import *
from alexandrie.forms import *

class EntityCreateView(CreateView):
    def form_invalid(self, form, error_msg=u"Erreur lors de l'enregistrement."):
        messages.error(self.request, error_msg)
        return super(EntityCreateView, self).form_invalid(form)

    def form_valid(self, form, success_msg=u"Enregistement effectué avec succès."):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        """
        entity = form.save(commit=False)
        entity.created_by = self.request.user
        entity.save()
        """
        form.instance.created_by = self.request.user
        messages.success(self.request, success_msg)
        return super(EntityCreateView, self).form_valid(form)

class EntityUpdateView(UpdateView):
    def form_invalid(self, form, error_msg=u"Erreur lors de l'enregistrement."):
        messages.error(self.request, error_msg)
        return super(EntityUpdateView, self).form_invalid(form)

    def form_valid(self, form, success_msg=u"Enregistement effectué avec succès."):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        """
        entity = form.save(commit=False)
        entity.modified_by = self.request.user
        entity.save()
        """
        form.instance.modified_by = self.request.user
        messages.success(self.request, success_msg)
        return super(EntityUpdateView, self).form_valid(form)


class HomeView(TemplateView):
    template_name = 'alexandrie/index.html'
    
    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        #context['category_list'] = Category.objects.all()
        return context


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

class ReaderBorrowDeleteView(DeleteView):
    template_name = 'alexandrie/confirm_delete.html'
    model = ReaderBorrow
    success_url = reverse_lazy('alexandrie:reader_borrow_list')

class ReaderBorrowListView(ListView):
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
                                  }
        )


class AuthorCreateView(EntityCreateView):
    template_name = 'alexandrie/author_detail.html'
    model = Author
    form_class = AuthorForm
    
    def form_valid(self, form):
        return super(AuthorCreateView, self).form_valid(form)

class AuthorUpdateView(EntityUpdateView):
    template_name = 'alexandrie/author_detail.html'
    model = Author
    form_class = AuthorForm

    def form_valid(self, form):
        return super(AuthorUpdateView, self).form_valid(form)

class AuthorDeleteView(DeleteView):
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

class AuthorListView(ListView):
    template_name = 'alexandrie/author_list.html'
    model = Author
    context_object_name = 'author_list'

    def search(request):
        last_name = request.POST['last_name']
        if (last_name != ''):
            author_list = Author.objects.filter(last_name__istartswith = last_name)
        else:
            author_list = Author.objects.all()
        return render_to_response(
            AuthorListView.template_name,
            {'author_list': author_list,},
            context_instance=RequestContext(request)
        )


class PublisherCreateView(EntityCreateView):
    template_name = 'alexandrie/publisher_detail.html'
    model = Publisher
    form_class = PublisherForm
    
    def form_valid(self, form):
        return super(PublisherCreateView, self).form_valid(form)

class PublisherUpdateView(EntityUpdateView):
    template_name = 'alexandrie/publisher_detail.html'
    model = Publisher
    form_class = PublisherForm

    def form_valid(self, form):
        return super(PublisherUpdateView, self).form_valid(form)

class PublisherDeleteView(DeleteView):
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

class PublisherListView(ListView):
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

class BookDeleteView(DeleteView):
    template_name = 'alexandrie/confirm_delete.html'
    model = Book
    success_url = reverse_lazy('alexandrie:book_list')

class BookListView(ListView):
    template_name = 'alexandrie/book_list.html'
    model = Book
    context_object_name = 'book_list'


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

class BookCopyDeleteView(DeleteView):
    template_name = 'alexandrie/confirm_delete.html'
    model = BookCopy

    def get_success_url(self):
        return self.object.book.get_absolute_url()


class ReaderCreateView(EntityCreateView):
    template_name = 'alexandrie/reader_detail.html'
    model = Reader
    form_class = ReaderForm
    
    def form_valid(self, form):
        return super(ReaderCreateView, self).form_valid(form)

class ReaderUpdateView(EntityUpdateView):
    template_name = 'alexandrie/reader_detail.html'
    model = Reader
    form_class = ReaderForm

    def form_valid(self, form):
        return super(ReaderUpdateView, self).form_valid(form)

class ReaderListView(ListView):
    template_name = 'alexandrie/reader_list.html'
    model = Reader
    context_object_name = 'reader_list'

class ReaderDisableView(EntityUpdateView):
    template_name = 'alexandrie/reader_disable.html'
    model = Reader
    form_class = ReaderDisableForm

    def form_valid(self, form):
        self.object.disabled_on = stddatetime.now()
        return super(ReaderDisableView, self).form_valid(form, u"Le lecteur a été désactivé avec succès.")

    def get_success_url(self):
        return self.object.get_absolute_url()

class ReaderListView(ListView):
    template_name = 'alexandrie/reader_list.html'
    model = Reader
    #queryset = Training.objects.order_by('-date')
    context_object_name = 'reader_list'
