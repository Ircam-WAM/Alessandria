#-*- encoding:utf-8 *-*
import unicodedata


class IsbnUtils(object):
    @staticmethod
    def author_unpack(author):
        if not author:
            return '', ''
        items = author.split    (' ')
        last_name = items[-1:][0]
        first_name = " ".join(items[:-1])
        return first_name, last_name
    
    @staticmethod
    def get_country_code(isbn_meta):
        if isbn_meta['Language']:
            return isbn_meta['Language'][:2].upper()
        return None

class MyString(object):
    @staticmethod
    def remove_accents(s):
        if s is None:
            return None
        return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')