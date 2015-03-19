#-*- encoding:utf-8 *-*

import datetime

from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.utils.safestring import mark_safe
from ajax_select.fields import AutoCompleteSelectField, AutoCompleteSelectMultipleField
from django_countries import countries

import bibli.settings as settings

from alexandrie.models import *

_l_countries = sorted(dict(countries).items())
_l_default_exclude_fields = ['created_by', 'created_on', 'modified_by', 'modified_on']
_css_class_required_field = 'required'


class CommonForm(forms.ModelForm):
    required_css_class = 'required' # Used in the template


class ReaderBorrowForm(CommonForm):
    class Meta:
        model = ReaderBorrow
        exclude = _l_default_exclude_fields

    borrow_due_date = forms.DateField(
        label=Meta.model._meta.get_field('borrow_due_date').verbose_name,
        initial= datetime.date.today() + datetime.timedelta(
            days=settings.GENERAL_CONFIGURATION.max_borrow_days
        )
    )
    bookcopy  = AutoCompleteSelectField('bookcopy_list', label=Meta.model._meta.get_field('bookcopy').verbose_name,
                                        required=True, help_text=None,
                                        plugin_options = {'autoFocus': True, 'minLength': 3})
    reader  = AutoCompleteSelectField('reader_list', label=Meta.model._meta.get_field('reader').verbose_name,
                                      required=True, help_text=None,
                                      plugin_options = {'autoFocus': True, 'minLength': 3})


class ReaderForm(CommonForm):
    class Meta:
        model = Reader
        exclude = _l_default_exclude_fields + ['number', 'disabled_on']

    country = forms.ChoiceField(
        label=Meta.model._meta.get_field('country').verbose_name,
        choices=_l_countries,
        initial=settings.GENERAL_CONFIGURATION.default_country
    )

class ReaderSearchForm(forms.ModelForm):
    class Meta:
        model = Reader
        fields = ('last_name',)

class ReaderDisableForm(CommonForm):
    class Meta:
        model = Reader
        fields = ()


class AuthorForm(CommonForm):
    class Meta:
        model = Author
        exclude = _l_default_exclude_fields + ['is_isbn_import', 'import_source']

    country = forms.ChoiceField(
        label=Meta.model._meta.get_field('country').verbose_name,
        choices=_l_countries,
        initial=settings.GENERAL_CONFIGURATION.default_country
    )

class AuthorSearchForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ('last_name',)


class PublisherForm(CommonForm):
    class Meta:
        model = Publisher
        exclude = _l_default_exclude_fields + ['is_isbn_import', 'import_source']

    country = forms.ChoiceField(
        label=Meta.model._meta.get_field('country').verbose_name,
        choices=_l_countries,
        initial=settings.GENERAL_CONFIGURATION.default_country
    )

class PublisherSearchForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ('name',)


class BookForm(CommonForm):
    def __init__(self, *args, **kwargs):
        super(BookForm, self).__init__(*args, **kwargs)
        self.initial['language'] = Language.get_default_language()

    title = forms.CharField(widget=forms.TextInput(attrs={'size': '40'}))
    class Meta:
        model = Book
        exclude = _l_default_exclude_fields + ['related_to', 'cover_pic', 'is_isbn_import']

    authors  = AutoCompleteSelectMultipleField(
                    'author_list', label=Meta.model._meta.get_field('authors').verbose_name,
                    required=True, help_text=u"Insérer les 1ères lettres du nom",
                    plugin_options = {'autoFocus': True, 'minLength': 3}
    )
    publishers  = AutoCompleteSelectMultipleField(
                    'publisher_list', label=Meta.model._meta.get_field('publishers').verbose_name,
                    required=True, help_text=u"Insérer les 1ères lettres du nom",
                    plugin_options = {'autoFocus': True, 'minLength': 3}
    )
    audiences = forms.ModelMultipleChoiceField(
                    widget=forms.CheckboxSelectMultiple(),
                    label=Meta.model._meta.get_field('audiences').verbose_name,
                    queryset=BookAudience.objects.all()
    )

class BookSearchForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ('title', 'category', 'sub_category',)


class BookCopyForm(CommonForm):
    class Meta:
        model = BookCopy
        exclude =  _l_default_exclude_fields + ['number', 'book', 'disabled_on']

    registered_on = forms.DateField(
        label=Meta.model._meta.get_field('registered_on').verbose_name, initial=datetime.date.today
    )

class BookCopyDisableForm(CommonForm):
    class Meta:
        model = BookCopy
        fields = ('disabled_on',)

    disabled_on = forms.DateField(
        label=Meta.model._meta.get_field('disabled_on').verbose_name,
        required=True
    )

    def clean(self):
        cleaned_data = super(BookCopyDisableForm, self).clean()