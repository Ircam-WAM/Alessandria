This is an application to manage a library.

How it works
============

Installation
------------
sudo pip install django
sudo pip install django-countries
sudo pip install django-ajax-selects
sudo pip install simplejson
sudo pip install pillow # To be able to upload images
sudo pip install isbnlib

sudo apt-get install sqlite3
mkdir db

Administration
--------------
1. Initialize database: ./manage.py migrate
2. ./manage.py loaddata --app alexandrie ref_data
3. Run the app : ./manage.py runserver
4. Go to the Django Admin page (e.g. http://127.0.0.1:8000/admin)
5. Set up initial data

Usage
-----
Just go to the start page (e.g. http://127.0.0.1:8000/alexandrie/).

Technical requirements
======================
* Django 1.7
* sqlite3
* Python 3