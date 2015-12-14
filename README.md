This is an application to manage a book library.

# Installation

## Prerequisites
* Django >= 1.7
* Python 3

## Get the sources and install alexandrie
<pre>git clone https://gitlab.com/openlabmatera/alexandrie.git
cd alexandrie
python setup.py sdist
pip install dist/django-alexandrie-<version>.tar.gz</pre>

## Django app - configuration
* Open the file *settings.py*
  * Add to your *INSTALLED_APPS* settings:
    <pre>
    INSTALLED_APPS = (
        ...
        'alexandrie',
        'alexandrie.templatetags.tag_extras',
        'ajax_select',
    )
    </pre>

* Open the file *urls.py* of your django project
  * Add this import at the beginning of the file:<pre>from ajax_select import urls as ajax_select_urls</pre>
  * Add to *urls_patterns*:<pre>urlpatterns = patterns('',
    ...
    url(r'^alexandrie/', include('alexandrie.urls', namespace='alexandrie')),
    url(r'^alexandrie/ajax_lookups/', include(ajax_select_urls)),
)</pre>
* Initialize database:<pre>./manage.py migrate
./manage.py loaddata --app alexandrie ref_data</pre>

## First run

* Run the app:<pre>./manage.py runserver</pre>
* Go to the Django Admin page (e.g. http://127.0.0.1:8000/admin) and log in as admin/admin
* Adapt configuration data to your needs (general configuration, book categories, ...)

# Usage

Just go to the start page (e.g. http://127.0.0.1:8000/alexandrie/).

