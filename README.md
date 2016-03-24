# Alexandrie: application de gestion d'une bibliothèque (english version below).

## Installation

### Prérequis
* Django >= 1.7
* Python 3
* Une base de données (ex. sqlite)

### Récupérer les sources et installer alexandrie
<pre>git clone https://gitlab.com/openlabmatera/alexandrie.git
cd alexandrie
python setup.py install</pre>

### Création d'un projet Django
Si vous ne souhaitez pas utiliser un projet Django existant, il faut en créer un:
<pre>django-admin startproject nom_du_projet</pre>

### Django app - configuration
* Dans le projet Django ouvrir le fichier *settings.py*
  * A *INSTALLED_APPS* ajouter:
    <pre>
    INSTALLED_APPS = (
        ...
        'alexandrie',
        'alexandrie.templatetags.tag_extras',
        'ajax_select',
    )
    </pre>

* Dans le projet Django, ouvrir le fichier *urls.py*
  * Ajouter cet import en début de fichier:<pre>from ajax_select import urls as ajax_select_urls</pre>
  * A *urls_patterns* ajouter:<pre>urlpatterns = patterns('',
    ...
    url(r'^alexandrie/', include('alexandrie.urls', namespace='alexandrie')),
    url(r'^alexandrie/ajax_lookups/', include(ajax_select_urls)),
)</pre>
* Initialiser la base de données:<pre>./manage.py migrate
./manage.py loaddata --app alexandrie ref_data</pre>

### Premier lancement

* Dans le projet Django lancer le serveur:<pre>./manage.py runserver</pre>
* Dans le navigateur aller sur la page d'administration du projet Django (http://127.0.0.1:8000/admin) et se connecter en tant que admin/admin
* Adapter la configuration de l'application à vos besoins: (configuration générale, catégorie des livres, ...)

## Utilisation
* Dans le navigateur, accéder à la page d'accueil: http://127.0.0.1:8000/alexandrie/

*****

Alexandrie: software to manage a book library.

## Installation 

### Prerequisites
* Django >= 1.7
* Python 3
* A database (e.g. sqlite)

### Get the sources and install alexandrie
<pre>git clone https://gitlab.com/openlabmatera/alexandrie.git
cd alexandrie
python setup.py install</pre>

### Setting up a Django project
If you don't want to use an existing django project, create one:
<pre>django-admin startproject my_project_name</pre>

### Django app - configuration
* In your django project, open the file *settings.py*
  * Add to your *INSTALLED_APPS* settings:
    <pre>
    INSTALLED_APPS = (
        ...
        'alexandrie',
        'alexandrie.templatetags.tag_extras',
        'ajax_select',
    )
    </pre>

* In your django project, open the file *urls.py* of your django project
  * Add this import at the beginning of the file:<pre>from ajax_select import urls as ajax_select_urls</pre>
  * Add to *urls_patterns*:<pre>urlpatterns = patterns('',
    ...
    url(r'^alexandrie/', include('alexandrie.urls', namespace='alexandrie')),
    url(r'^alexandrie/ajax_lookups/', include(ajax_select_urls)),
)</pre>
* Initialize database:<pre>./manage.py migrate
./manage.py loaddata --app alexandrie ref_data</pre>

### First run

* Launch the Django server:<pre>./manage.py runserver</pre>
* In your browser, go to the Django Admin page: http://127.0.0.1:8000/admin and log in as admin/admin
* Adapt configuration data to your needs (general configuration, book categories, ...)

## Usage

* In your browser go to the start page: http://127.0.0.1:8000/alexandrie/
