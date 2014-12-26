"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from alexandrie.models import Book

class BookTest(TestCase):
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