This is an application to manage a book library.


# Installation
## Prerequisites
* Django >= 1.7
* Python 3
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
  * At the end of the file, add:<pre>
    from alexandrie.local_settings import *</pre>
* Open the file *urls.py* of your django project and add to *urls_patterns*:<pre>urlpatterns = patterns('',
    ...
    url(r'^alexandrie/', include('alexandrie.urls', namespace='alexandrie')),
)</pre>
* Initialize database:<pre>./manage.py migrate
./manage.py loaddata --app alexandrie ref_data</pre>

## First run

* Run the app:<pre>./manage.py runserver</pre>
* Go to the Django Admin page (e.g. http://127.0.0.1:8000/admin)
* Enter initial data (general configuration, book categories, ...)

# Usage

Just go to the start page (e.g. http://127.0.0.1:8000/alexandrie/).

