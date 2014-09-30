#-*- encoding:utf-8 *-*
import datetime

from django import forms
from django.forms.util import flatatt
from django.utils.safestring import mark_safe

from alexandrie.models import *

class ReaderForm(forms.ModelForm):
    class Meta:
        model = Reader


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ('first_name', 'last_name', 'birth_year', 'country', 'notes')


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        #fields = ('first_name', 'last_name', 'birth_year', 'country', 'notes')
        #exclude = ('created_by', 'created_on', 'modified_by', 'modified_on')


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
