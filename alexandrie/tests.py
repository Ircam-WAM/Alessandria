# -*- coding: utf-8 -*-

"""
Tests of the software
"""

from datetime import date, datetime, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth.models import User

import isbnlib

from alexandrie.models import *


class GenericTest(TestCase):
    def setUp(self):
        self.user = self.create_user()

    def create_book(self, inst_nb, isbn_nb=None):
        language = Language.objects.create(label='FR')
        category1 = BookCategory.objects.create(label="cat%s" % inst_nb)
        sub_category1 = BookSubCategory.objects.create(label="s_cat%s" % inst_nb, parent_category=category1)
        audience1 = BookAudience.objects.create(label="Children%s" % inst_nb)
        book = Book(
            title="Hello world%s" % inst_nb,
            language = language,
            publish_date=datetime.today(),
            category = category1,
            sub_category = sub_category1,
            classif_mark="abc%s" % inst_nb,
            height=21,
            isbn_nb = isbn_nb
        )
        book.created_by = self.user
        book.created_on = datetime.today()
        book.save()
        book.audiences.add(audience1)
        book.authors.add(self.create_author(inst_nb))
        book.publishers.add(self.create_publisher(inst_nb))
        book.save()
        return book
    
    def create_reader(self, inst_nb, profession=None):
        r = Reader()
        r.first_name = "fn%s" % inst_nb
        r.last_name = "ln%s" % inst_nb
        r.addr1 = "addr%s" % inst_nb
        r.zip = "%s" % inst_nb
        r.city = "city%s" % inst_nb
        r.country = "FR"
        r.inscription_date = datetime.today()
        r.birthday = '1971-03-24'
        if profession is None:
            profession = Profession(label='p%s' % inst_nb)
        r.profession = profession
        r.sex = 'm'
        r.created_by = self.user
        r.created_on = datetime.today()
        r.save()
        return r
    
    def create_author(self, inst_nb):
        a = Author()
        a.first_name = "fn%s" % inst_nb
        a.last_name = "ln%s" % inst_nb
        a.country = 'FR'
        a.created_by = self.user
        a.created_on = datetime.today()
        a.save()
        return a
    
    def create_publisher(self, inst_nb):
        p = Publisher()
        p.name = "n%s" % inst_nb
        p.country = 'FR'
        p.created_by = self.user
        p.created_on = datetime.today()
        p.save()
        return p
    
    def create_user(self, first_name='lucie', last_name='fer', username='luciefer', email='lucie@hell.com'):
        return User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email)

class BookTest(GenericTest):
    def setUp(self):
        super(BookTest, self).setUp()

    def tearDown(self):
        pass

    def test_create_update_book(self):
        # Test create
        b_count = Book.objects.count()
        b1 = self.create_book('1')
        self.assertEqual(Book.objects.count(), b_count + 1)

        # Test update
        b_u = Book.objects.filter(id=b1.id).first()
        b_u.classif_mark = 'm_classif'
        b_u.save()
        self.assertTrue(len(Book.objects.filter(classif_mark='m_classif')) > 0)

    def test_isbn(self):
        b2 = self.create_book('2', isbn_nb='9783037680582')
        self.assertIsNot(b2, None)
        
        b2.isbn_nb = 'wrong_isbn'
        with self.assertRaises(ValidationError):
            b2.save()

    def test_isbn_lib(self):
        """Ensure the isbnlib works but also show use cases"""
        isbn_nb = '978-3-03768-058-2'
        self.assertTrue(isbnlib.is_isbn13(isbn_nb))
        self.assertEqual(isbnlib.get_canonical_isbn(isbn_nb), '9783037680582')
        self.assertIsNone(isbnlib.get_canonical_isbn('notisbn'))
        self.assertIsNone(isbnlib.get_canonical_isbn('12345'))
        isbn_meta = isbnlib.meta(isbn_nb)
        self.assertTrue(isbn_meta['Title'].startswith('The Tourist City Berlin'))
        self.assertEqual(isbn_meta['Publisher'], 'Braun')
        self.assertEqual(isbn_meta['Authors'][0], 'Jana Richter')
        self.assertEqual(isbn_meta['Language'], 'eng')
        self.assertEqual(isbn_meta['Year'], '2010')

class ReaderTest(GenericTest):
    def setUp(self):
        super(ReaderTest, self).setUp()

    def tearDown(self):
        pass

    def test_create(self):
        prof1 = Profession(label='p1')
        prof2 = Profession(label='p2')

        r1 = self.create_reader(1, prof1)
        self.assertEqual(r1.number, 1)
        self.assertEqual(Reader.objects.filter(last_name='ln1').count(), 1)

        r2 = self.create_reader(2, prof2)
        self.assertEqual(r2.number, 2)
        self.assertEqual(Reader.objects.filter(first_name='fn2').count(), 1)

        r2.addr2 = 'addr2 added'
        r2.modified_by = self.user
        r2.save()
        r2_mod = Reader.objects.filter(number=2).first()
        self.assertEqual(r2_mod.addr2, r2.addr2)

class AppliNewsTest(GenericTest):
    def setUp(self):
        pass
    
    def test_create_and_list(self):
        n1 = AppliNews(publish_date=date.today() + timedelta(days=-1), news="Hello1")
        n1.save()
        n2 = AppliNews(publish_date=date.today(), news="Hello2")
        n2.save()
        self.assertEqual(AppliNews.objects.count(), 2)
        self.assertEqual(AppliNews.get_last().news, "Hello2")
        n_future = AppliNews(publish_date=date.today() + timedelta(days=2), news="Hello future")
        n_future.save()
        self.assertEqual(AppliNews.objects.count(), 3)
        # Make sure we don't retrieve news that will be published in the future
        self.assertEqual(len(AppliNews.list()), 2)
        self.assertEqual(AppliNews.get_last().news, "Hello2")
