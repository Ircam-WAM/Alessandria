from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.forms.models import inlineformset_factory
from django.views.generic.base import TemplateView, View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from alexandrie.models import *
from alexandrie.forms import *

class EntityCreateView(CreateView):
    pass

class HomeView(TemplateView):
    template_name = 'alexandrie/index.html'
    
    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        #context['category_list'] = Category.objects.all()
        return context


class AuthorCreateView(CreateView):
    template_name = 'alexandrie/author_detail.html'
    model = Author
    form_class = AuthorForm
    #fields = ['first_name']
    
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        author = form.save(commit=False)
        author.created_by = self.request.user
        author.save()
        return super(AuthorCreate, self).form_valid(form)


class AuthorUpdateView(UpdateView):
    template_name = 'alexandrie/author_detail.html'
    model = Author
    form_class = AuthorForm


class AuthorListView(ListView):
    template_name = 'alexandrie/author_list.html'
    model = Author
    context_object_name = 'author_list'


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
