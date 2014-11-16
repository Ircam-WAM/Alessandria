from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.forms.models import inlineformset_factory
from django.views.generic.base import TemplateView, View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages

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

class BookCopyDeleteView(DeleteView):
    template_name = 'alexandrie/confirm_delete.html'
    model = BookCopy

    def get_success_url(self):
        return self.object.book.get_absolute_url()

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


class ReaderView(View):
    def get(self, request, training_id=None):
        if reader_id:
            # Update mode
            reader = get_object_or_404(Reader, id=reader_id)
        else:
            # Add mode
            pass
        return self._display_template(request)
    
    def post(self, request, training_id=None):
        reader = None
        if reader_id:
            # Update existing training
            reader = get_object_or_404(Reader, id=reader_id)
        """
        if self.training_form.is_valid() and self.player_form_set.is_valid():
            training = self.training_form.save()
            self.player_form_set.instance = training
            self.player_form_set.save()
            return HttpResponseRedirect(training.get_absolute_url())
        else:
            self.coach_form = TrainingCoachForm() ### CHANGE ME! ###
            return self._display_template(request)
        """
    def _display_template(self, request):
        context = {
        }
        return render(request, 'alexandrie/reader.html', context)


class ReaderListView(ListView):
    template_name = 'alexandrie/reader_list.html'
    model = Reader
    #queryset = Training.objects.order_by('-date')
    context_object_name = 'reader_list'
