# Alessandria: application de gestion d'une bibliothèque (english version below).

## Installation

### Prérequis
* Django <= 1.11
* Python 3
* Une base de données (ex. sqlite)

### Récupérer les sources et installer alessandria
```
git clone https://gitlab.com/openlabmatera/alessandria.git
cd alessandria
python setup.py install
```

* Remarque: si vous avez des erreurs concernant l'installation du module *pillow*, c'est probablement parcequ'il vous manque des bibliothèques système. Pour Debian Jessie, il faut exécuter:
```
apt-get install libjpeg-dev libghc-zlib-dev
```

### Création d'un projet Django
Si vous ne souhaitez pas utiliser un projet Django existant, il faut en créer un:
```
django-admin startproject nom_du_projet
```

### Django app - configuration
* Dans le projet Django ouvrir le fichier *settings.py*
  * A *INSTALLED_APPS* ajouter:
```
    INSTALLED_APPS = (
        ...
        'alessandria',
        'alessandria.templatetags.tag_extras',
        'ajax_select',
    )
```

* Dans le projet Django, ouvrir le fichier *urls.py*
  * Ajouter cet import en début de fichier:
```
from   ajax_select import urls as ajax_select_urls
```
     
  * A *urls_patterns* ajouter:
```
urlpatterns   = patterns('',
    ...
    url(r'^alessandria/', include('alessandria.urls', namespace='alessandria')),
    url(r'^alessandria/ajax_lookups/', include(ajax_select_urls)),
)
```

* Initialiser la base de données:
```
./manage.py migrate
./manage.py loaddata --app alessandria ref_data_fr
```

### Premier lancement

* Dans le projet Django lancer le serveur:
```
./manage.py runserver
```

* Dans le navigateur aller sur la page d'administration du projet Django (http://127.0.0.1:8000/admin) et se connecter en tant que admin/admin
* Adapter la configuration de l'application à vos besoins: (configuration générale, catégorie des livres, ...)

## Utilisation
* Dans le navigateur, accéder à la page d'accueil: http://127.0.0.1:8000/alessandria/

*****

# Alessandria: software to manage a book library.

## Installation 

### Prerequisites
* Django <= 1.11
* Python 3
* A database (e.g. sqlite)

### Get the sources and install alessandria
```
git clone https://gitlab.com/openlabmatera/alessandria.git
cd alessandria
python setup.py install
```

* Note: if you get errors while the *pillow* module is being installed, it's probably because some libraries are missing on your system. On Debian Jessie, execute:
```
apt-get install libjpeg-dev libghc-zlib-dev
```

### Setting up a Django project
If you don't want to use an existing django project, create one:
```
django-admin startproject my_project_name
```

### Django app - configuration
* In your django project, open the file *settings.py*
  * Add to your *INSTALLED_APPS* settings:
```
INSTALLED_APPS = (
	...
	'alessandria',
	'alessandria.templatetags.tag_extras',
	'ajax_select',
)
```

* In your django project, open the file *urls.py* of your django project
  * Add this import at the beginning of the file:
  ```
from   ajax_select import urls as ajax_select_urls
```
  * Add to *urls_patterns*:
```
urlpatterns = patterns('',
	...
	url(r'^alessandria/', include('alessandria.urls', namespace='alessandria')),
	url(r'^alessandria/ajax_lookups/', include(ajax_select_urls)),
)
```
* Initialize the database:
```./manage.py migrate
./manage.py loaddata --app alessandria ref_data
```

### First run

* Launch the Django server:
```
./manage.py runserver
```
* In your browser, go to the Django Admin page: http://127.0.0.1:8000/admin and log in as admin/admin
* Adapt configuration data to your needs (general configuration, book categories, ...)

## Usage

* In your browser go to the start page: http://127.0.0.1:8000/alessandria/
