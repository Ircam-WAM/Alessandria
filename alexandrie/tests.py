# -*- coding: utf-8 -*-

"""
Tests of the software
"""

from datetime import date, datetime, timedelta

from django.test import TestCase
from django.contrib.auth.models import User

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
            height=21
        )
        book.created_by = self.user
        book.created_on = datetime.today()
        book.save()
        book.audiences.add(audience1)
        book.authors.add(self.create_author('1'))
        book.publishers.add(self.create_publisher('1'))
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

    def test_create_book(self):
        b1 = self.create_book('1')
        self.assertEqual(Book.objects.count(), 1)

    """
    title = models.CharField(u"Titre", max_length=50)
    authors = models.ManyToManyField(Author, verbose_name=u'Auteurs')
    publishers = models.ManyToManyField(Publisher, verbose_name=u'Editeurs')
    publish_date = models.DateField(u"Date d'édition")
    edition_name = models.CharField(u"Titre édition", max_length=80, null=True, blank=True)
    classif_mark = models.CharField(u"Cote", max_length=10)
    height = models.PositiveIntegerField(u"Hauteur (cm)", max_length=3)
    isbn_nb = models.CharField(u"No. ISBN", max_length=20, null=True, blank=True, unique=True)
    audiences = models.ManyToManyField(BookAudience, verbose_name=u'Public cible')
    category = models.ForeignKey(BookCategory, verbose_name=u'Catégorie')
    sub_category = models.ForeignKey(BookSubCategory, null=True, blank=True, verbose_name=u'Sous-catégorie')
    abstract = models.TextField(u"Résumé", null=True, blank=True)
    tags = models.ManyToManyField(BookTag, verbose_name=u'Etiquettes', null=True, blank=True)
    language = models.ForeignKey(Language, default=get_default_language, verbose_name=u'Langue')
    cover_pic = models.ImageField(verbose_name=u'Couverture', upload_to='alexandrie/upload', null=True, blank=True)
    related_to = models.ForeignKey('Book', null=True, blank=True, verbose_name=u"Apparenté à")
    notes = models.TextField(u"Notes", null=True, blank=True)
    """

    def test_isbn_strip(self):
        self.assertEqual(Book.strip_isbn('2-266-11156-5'), '2266111565')

    def test_check_isbn_valid(self):
        self.assertEqual(Book.check_isbn_valid(''), '')
        self.assertEqual(Book.check_isbn_valid('2-266-11156-5'), '')
        self.assertEqual(Book.check_isbn_valid('2266111565'), '')
        self.assertEqual(Book.check_isbn_valid('978-2-86889-006-1'), '')
        self.assertEqual(Book.check_isbn_valid('9782868890061'), '')
        self.assertEqual(Book.check_isbn_valid('978-2-10-058178-8'), '')
        self.assertEqual(Book.check_isbn_valid('978-2-258-07349-4'), '')
        self.assertNotEqual(Book.check_isbn_valid('978-2'), '')

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
