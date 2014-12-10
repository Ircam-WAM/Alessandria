#-*- encoding:utf-8 *-*
import datetime

from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.utils.safestring import mark_safe
from ajax_select.fields import AutoCompleteSelectField, AutoCompleteSelectMultipleField

import bibli.settings as settings

from alexandrie.models import *


class ReaderBorrowForm(forms.ModelForm):
    class Meta:
        model = ReaderBorrow

    borrow_due_date = forms.DateField(
        label=Meta.model._meta.get_field('borrow_due_date').verbose_name,
        initial= datetime.date.today() + datetime.timedelta(
            days=settings.GENERAL_CONFIGURATION.max_borrow_days
        )
    )

    class Meta:
        model = ReaderBorrow
        exclude = ('created_by', 'created_on', 'modified_by', 'modified_on', 'disabled_on',)

    bookcopy  = AutoCompleteSelectField('bookcopy_list', label=Meta.model._meta.get_field('bookcopy').verbose_name,
                                        required=True, help_text=None,
                                        plugin_options = {'autoFocus': True, 'minLength': 3})

    reader  = AutoCompleteSelectField('reader_list', label=Meta.model._meta.get_field('reader').verbose_name,
                                      required=True, help_text=None,
                                      plugin_options = {'autoFocus': True, 'minLength': 3})


class ReaderForm(forms.ModelForm):
    class Meta:
        model = Reader
        exclude = ('created_by', 'created_on', 'modified_by', 'modified_on', 'disabled_on')

class ReaderSearchForm(forms.ModelForm):
    class Meta:
        model = Reader
        fields = ('last_name',)


class ReaderDisableForm(forms.ModelForm):
    class Meta:
        model = Reader
        fields = ()


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ('first_name', 'last_name', 'birth_year', 'country', 'notes')

class AuthorSearchForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ('last_name',)


class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ('name', 'country', 'notes')


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        exclude = ('created_by', 'created_on', 'modified_by', 'modified_on')

    authors  = AutoCompleteSelectMultipleField(
                    'author_list', label=Meta.model._meta.get_field('authors').verbose_name,
                    required=True, help_text=None,
                    plugin_options = {'autoFocus': True, 'minLength': 3}
    )
    audiences = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple(attrs={'class': 'list-unstyled'}),
        queryset=BookAudience.objects.all())

class BookSearchForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ('title', 'category', 'sub_category',)


class BookCopyForm(forms.ModelForm):
    class Meta:
        model = BookCopy
        fields = ('number', 'registered_on', 'condition', 'is_bought', 'price', 'price_date')
        #exclude = ('created_by', 'created_on', 'modified_by', 'modified_on', 'book')
    
    registered_on = forms.DateField(
        label=Meta.model._meta.get_field('registered_on').verbose_name, initial=datetime.date.today)

class BookCopyDisableForm(forms.ModelForm):
    class Meta:
        model = BookCopy
        fields = ('disabled_on',)

    disabled_on = forms.DateField(
        label=Meta.model._meta.get_field('disabled_on').verbose_name, required=True)
    
    def clean(self):
        cleaned_data = super(BookCopyDisableForm, self).clean()