#-*- encoding:utf-8 *-*
import datetime

from django import forms

from django.forms.extras.widgets import SelectDateWidget

from django.utils.safestring import mark_safe

from alexandrie.models import *


class ReaderBorrowForm(forms.ModelForm):
    class Meta:
        model = ReaderBorrow
        exclude = ('created_by', 'created_on', 'modified_by', 'modified_on', 'disabled_on')

    bookcopy = forms.ModelChoiceField(queryset=BookCopy.objects.filter(disabled_on=None),
                                      label=Meta.model._meta.get_field('bookcopy').verbose_name)
    reader = forms.ModelChoiceField(queryset=Reader.objects.filter(disabled_on=None),
                                      label=Meta.model._meta.get_field('reader').verbose_name)


class ReaderForm(forms.ModelForm):
    class Meta:
        model = Reader
        exclude = ('created_by', 'created_on', 'modified_by', 'modified_on', 'disabled_on')


class ReaderDisableForm(forms.ModelForm):
    class Meta:
        model = Reader
        fields = ()


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ('first_name', 'last_name', 'birth_year', 'country', 'notes')


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        exclude = ('created_by', 'created_on', 'modified_by', 'modified_on')

    audiences = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple(attrs={'class': 'list-unstyled'}),
        queryset=BookAudience.objects.all())


class BookCopyForm(forms.ModelForm):
    class Meta:
        model = BookCopy
        fields = ('number', 'registered_on', 'condition', 'is_bought', 'price', 'price_date')
        #exclude = ('created_by', 'created_on', 'modified_by', 'modified_on', 'book')
    
    registered_on = forms.DateField(
        label=Meta.model._meta.get_field('registered_on').verbose_name, widget=SelectDateWidget(),
        initial=datetime.date.today)

class BookCopyDisableForm(forms.ModelForm):
    class Meta:
        model = BookCopy
        fields = ('disabled_on',)

    disabled_on = forms.DateField(
        label=Meta.model._meta.get_field('disabled_on').verbose_name, required=True)
    
    def clean(self):
        cleaned_data = super(BookCopyDisableForm, self).clean()

'''
class GameForm(forms.ModelForm):
    
    class Meta:
        model = Game


class TrainingForm(forms.ModelForm):
    date = forms.DateField(initial=datetime.date.today)
    categories = forms.ModelMultipleChoiceField(
                widget=MyCheckboxSelectMultiple(ul_attrs={"class":"unstyled"}), 
                required=True, 
                queryset=Category.objects.all(),
                label=u'Catégories',
            )

    themes = forms.ModelMultipleChoiceField(
                widget=MyCheckboxSelectMultiple(ul_attrs={"class":"unstyled"}), 
                required=True, 
                queryset=TrainingTheme.objects.all(),
                label=u'Thèmes',
            )

    class Meta:
        model = Training
        exclude = ('added_by', 'updated_by', 'players', 'coaches')
        widgets = {
            'notes': forms.Textarea(attrs={'cols': 80, 'rows': 5}),
        }        
        

class TrainingPlayerForm(forms.ModelForm):
    class Meta:
        model = TrainingPlayer
        exclude = ('training',)
        widgets = {
            'comment': forms.Textarea(attrs={'cols': 30, 'rows': 1}),
        }

class TrainingCoachForm(forms.ModelForm):
    class Meta:
        model = TrainingCoach
        exclude = ('training',)
'''
