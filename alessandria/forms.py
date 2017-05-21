import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.db.utils import OperationalError
from ajax_select.fields import AutoCompleteSelectField, AutoCompleteSelectMultipleField
from django_countries import countries

from alessandria.models import (
    GeneralConfiguration, ReaderBorrow, Reader, Author, Publisher, Book, BookAudience, BookCopy
)


max_borrow_days = 0
default_country = None
try:
    if GeneralConfiguration.objects.first() is not None:
        max_borrow_days = GeneralConfiguration.objects.first().max_borrow_days
except OperationalError:
    # To prevent "django.db.utils.OperationalError" when reseting the DB
    pass

_l_countries = sorted(dict(countries).items())
_l_default_exclude_fields = ['created_by', 'created_on', 'modified_by', 'modified_on']
_css_class_required_field = 'required'


class CommonForm(forms.ModelForm):
    required_css_class = 'required'  # Used in the template


class ReaderBorrowForm(CommonForm):
    class Meta:
        model = ReaderBorrow
        exclude = _l_default_exclude_fields
    borrowed_date = forms.DateField(
        label=Meta.model._meta.get_field('borrowed_date').verbose_name,
        initial=datetime.date.today()
    )
    borrow_due_date = forms.DateField(
        label=Meta.model._meta.get_field('borrow_due_date').verbose_name,
        initial=datetime.date.today() + datetime.timedelta(days=max_borrow_days)
    )

    # 'bookcopy_list' and 'reader_list' are registered lookups.py
    bookcopy = AutoCompleteSelectField(
        'bookcopy_list', label=Meta.model._meta.get_field('bookcopy').verbose_name,
        required=False, help_text=None, plugin_options={'autoFocus': True, 'minLength': 3}
    )
    reader = AutoCompleteSelectField(
        'reader_list', label=Meta.model._meta.get_field('reader').verbose_name,
        required=False, help_text=None, plugin_options={'autoFocus': True, 'minLength': 3}
    )

    def clean_reader(self):
        if self.cleaned_data['reader'] is None:
            raise forms.ValidationError(_("Please select a reader"))
        return self.cleaned_data['reader']

    def clean_bookcopy(self):
        bookcopy = self.cleaned_data['bookcopy']
        if bookcopy is None:
            raise forms.ValidationError(_("Please select a a book copy"))
        # Make sure this bookcopy was not already borrowed by somebody else
        already_borrowed = ReaderBorrow.objects.filter(bookcopy=bookcopy).filter(returned_on=None).first()
        error = False
        if already_borrowed is not None:
            if self.instance is not None:  # Update mode
                if already_borrowed.id != self.instance.id:  # Not updating the current record
                    error = True
            else:  # Create mode
                error = True
            if error:
                raise forms.ValidationError(
                    _('This book copy was already borrowed by {0}.').format(already_borrowed.reader)
                )
        return bookcopy


class ReaderForm(CommonForm):
    class Meta:
        model = Reader
        exclude = _l_default_exclude_fields + ['number', 'disabled_on']

    country = forms.ChoiceField(
        label=Meta.model._meta.get_field('country').verbose_name,
        choices=_l_countries,
        initial=default_country
    )

    def clean(self):
        cleaned_data = super().clean()

        homonyms = Reader.objects.filter(
            first_name__iexact=cleaned_data.get("first_name")
        ).filter(
            last_name__iexact=cleaned_data.get("last_name")
        ).filter(
            birthday=cleaned_data.get("birthday")
        ).filter(
            city__iexact=cleaned_data.get("city")
        )
        if homonyms.exists():
            self.add_error('last_name', _("This reader already exists."))


class ReaderSearchForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override the fields making it NOT mandatory
        self.fields['last_name'].required = False

    reader_enabled = forms.BooleanField(label=_("Readers enabled"), initial=True, required=False)

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
        initial=default_country
    )

    def clean(self):
        cleaned_data = super().clean()

        homonyms = Author.objects.filter(
            first_name__iexact=cleaned_data.get("first_name")
        ).filter(
            last_name__iexact=cleaned_data.get("last_name")
        ).filter(
            birthday=cleaned_data.get("birthday")
        )
        if homonyms.exists():
            self.add_error('last_name', _("This author already exists."))


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
        initial=default_country
    )


class PublisherSearchForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ('name',)


class BookForm(CommonForm):

    class Meta:
        model = Book
        exclude = _l_default_exclude_fields + ['related_to', 'cover_pic']

    title = forms.CharField(
        label=Meta.model._meta.get_field('title').verbose_name,
        widget=forms.TextInput(attrs={'size': '40'})
    )

    # 'author_list' and 'publisher_list' are registered lookups.py
    authors = AutoCompleteSelectMultipleField(
        'author_list', label=Meta.model._meta.get_field('authors').verbose_name,
        required=False, help_text=None, plugin_options={'autoFocus': True, 'minLength': 3}
    )
    publishers = AutoCompleteSelectMultipleField(
        'publisher_list', label=Meta.model._meta.get_field('publishers').verbose_name,
        required=False, help_text=None, plugin_options={'autoFocus': True, 'minLength': 3}
    )
    audiences = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(), label=Meta.model._meta.get_field('audiences').verbose_name,
        queryset=BookAudience.objects.all()
    )

    def clean_authors(self):
        if not any(self.cleaned_data['authors']):  # It is a list
            raise forms.ValidationError(_("Please select at least one author"))
        return self.cleaned_data['authors']

    def clean_publishers(self):
        if not any(self.cleaned_data['publishers']):  # It is a list
            raise forms.ValidationError(_("Please select at least one publisher"))
        return self.cleaned_data['publishers']


class BookSearchForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override the fields making it NOT mandatory
        self.fields['isbn_nb'].required = False
        self.fields['title'].required = False
        self.fields['category'].required = False

    author_name = forms.CharField(label=_('Author'), required=False)
    has_copy = forms.BooleanField(label=_('Has copy'), initial=True)
    took_away = forms.BooleanField(label=_('Took away'), initial=False, required=False)

    class Meta:
        model = Book
        fields = ('isbn_nb', 'title', 'category', 'sub_category',)


class BookCopyForm(CommonForm):
    class Meta:
        model = BookCopy
        exclude = _l_default_exclude_fields + ['number', 'book', 'disabled_on']

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

