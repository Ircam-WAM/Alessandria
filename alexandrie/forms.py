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
        exclude = ('number', 'created_by', 'created_on', 'modified_by', 'modified_on', 'disabled_on')

    country = forms.ChoiceField(
        label=Meta.model._meta.get_field('country').verbose_name,
        choices=_l_countries,
        initial=settings.GENERAL_CONFIGURATION.default_country
    )

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
        fields = ('first_name', 'last_name', 'country', 'website', 'notes')

    country = forms.ChoiceField(
        label=Meta.model._meta.get_field('country').verbose_name,
        choices=_l_countries,
        initial=settings.GENERAL_CONFIGURATION.default_country
    )

class AuthorSearchForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ('last_name',)


class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ('name', 'country', 'notes')

    country = forms.ChoiceField(
        label=Meta.model._meta.get_field('country').verbose_name,
        choices=_l_countries,
        initial=settings.GENERAL_CONFIGURATION.default_country
    )

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        # TODO: enable cover_pic again
        exclude = ('cover_pic', 'created_by', 'created_on', 'modified_by', 'modified_on')

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


class BookCopyForm(forms.ModelForm):
    class Meta:
        model = BookCopy
        fields = ('registered_on', 'condition', 'is_bought', 'price', 'price_date')

    registered_on = forms.DateField(
        label=Meta.model._meta.get_field('registered_on').verbose_name, initial=datetime.date.today
    )

class BookCopyDisableForm(forms.ModelForm):
    class Meta:
        model = BookCopy
        fields = ('disabled_on',)

    disabled_on = forms.DateField(
        label=Meta.model._meta.get_field('disabled_on').verbose_name,
        required=True
    )

    def clean(self):
        cleaned_data = super(BookCopyDisableForm, self).clean()