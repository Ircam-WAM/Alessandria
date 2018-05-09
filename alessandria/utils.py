#-*- encoding:utf-8 *-*
import unicodedata
import uuid
from django.apps import apps

class IsbnUtils(object):
    @staticmethod
    def author_unpack(author):
        if not author:
            return '', ''
        items = author.split    (' ')
        last_name = items[-1:][0].strip()
        first_name = " ".join(items[:-1]).strip()
        return first_name, last_name
    
    @staticmethod
    def get_country_code(isbn_meta):
        if isbn_meta['Language']:
            return isbn_meta['Language'][:2].upper()
        return None
    
    @staticmethod
    def get_isbn_nb_from_meta(isbn_meta):
        if isbn_meta is not None:
            if isbn_meta.get('ISBN-13'):
                return isbn_meta['ISBN-13']
            if isbn_meta.get('ISBN-10'):
                return isbn_meta['ISBN-10']
        return None

class MyString(object):
    @staticmethod
    def remove_accents(s):
        if s is None:
            return None
        return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def generate_book_uuid():
    
    Book = apps.get_model('alessandria','Book')
    b_uuid = ""
    while True :
        b_uuid = str(uuid.uuid4())[:5]   
        if not Book.objects.filter(_uuid=b_uuid):
            break;
    return b_uuid