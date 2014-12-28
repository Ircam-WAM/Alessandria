"""
Tests of the software
"""

from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from alexandrie.models import Book, Reader, Profession

class GenericTest(TestCase):
    def setUp(self):
        pass

class BookTest(GenericTest):
    def setUp(self):
        pass

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
        self.user = User.objects.create_user('lucie', 'lucie@hell.com', 'luciefer')

    def _create_reader(self, inst_nb, profession):
        r = Reader()
        r.first_name = "fn%s" % inst_nb
        r.last_name = "ln%s" % inst_nb
        r.addr1 = "addr%s" % inst_nb
        r.zip = "%s" % inst_nb
        r.city = "city%s" % inst_nb
        r.country = "FR"
        r.inscription_date = datetime.today()
        r.profession = profession
        r.created_by = self.user
        r.created_on = datetime.today()
        r.save()
        return r

    def test_create(self):
        prof1 = Profession(label='p1')
        prof2 = Profession(label='p2')

        r1 = self._create_reader(1, prof1)
        self.assertEqual(r1.number, 1)
        self.assertEqual(Reader.objects.filter(last_name='ln1').count(), 1)

        r2 = self._create_reader(2, prof2)
        self.assertEqual(r2.number, 2)
        self.assertEqual(Reader.objects.filter(first_name='fn2').count(), 1)

        r2.addr2 = 'addr2 added'
        r2.save()
        r2_mod = Reader.objects.filter(number=2).first()
        self.assertEqual(r2_mod.addr2, r2.addr2)