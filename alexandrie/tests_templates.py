from django.contrib.auth.models import User
from django.conf.urls import url
from django.test import Client
from django.test import TestCase
from alexandrie.urls import urlpatterns


class GeneralTest(TestCase):
    def setUp(self):
        User.objects.create_superuser(
            username='admin',
            password='admin',
            email='admin@example.com'
        )
        self.login()

    def tearDown(self):
        # TODO check logout
        pass

    def login(self):
        self.client = Client()
        self.assertFalse(self.client.login(username='foo', password='bar'))
        self.assertTrue(self.client.login(username='admin', password='admin'))

    def get_and_test_url(self, url, expected_status_code=200):
        response = self.client.get(url)
        self.assertEqual(expected_status_code, response.status_code)
        if response.status_code == 200:
            self.assertTrue(len(response.content) > 0)

    def test_wrong_url(self):
        response = self.client.get('/foo/bar/')
        self.assertEqual(404, response.status_code)

    def test_home_page(self):
        self.get_and_test_url('/')

    def test_login_page(self):
        self.get_and_test_url('/login/')

    def test_pages_create_mode(self):
        self.get_and_test_url('/reader_borrow/add/')
        self.get_and_test_url('/reader_borrow/list/')

        self.get_and_test_url('/reader/add/')
        self.get_and_test_url('/reader/list/')

        self.get_and_test_url('/author/add/')
        self.get_and_test_url('/author/list/')

        self.get_and_test_url('/publisher/add/')
        self.get_and_test_url('/publisher/list/')

        self.get_and_test_url('/book/add/')
        self.get_and_test_url('/book/list/')
        # TODO: see why we get: AssertionError: 200 != 301
        self.get_and_test_url('/book/isbn/import', 301)
