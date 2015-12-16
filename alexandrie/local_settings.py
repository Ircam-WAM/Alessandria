# -*- coding: utf-8 -*-

"""
Django settings for the alexandrie app.
"""

from django.conf import settings
from django.db.utils import OperationalError

context_processors = settings.TEMPLATES[0]['OPTIONS']['context_processors']
# Used for i18n of jquery date picker plugin (http://keith-wood.name/datepick.html)
context_processors.append("alexandrie.context_processors.js_datepicker_lang")
context_processors.append("alexandrie.context_processors.app_version")
context_processors.append("alexandrie.context_processors.library_infos")

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'alexandrie.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers':['file'],
            'propagate': True,
            'level':'INFO',
        },
        'alexandrie': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    }
}

try:
    from alexandrie.models import GeneralConfiguration
    GENERAL_CONFIGURATION = GeneralConfiguration.get()
    LIBRARY_INFOS = {
        'name': GENERAL_CONFIGURATION.library_name,
        'addr1': GENERAL_CONFIGURATION.library_addr1,
        'addr2': GENERAL_CONFIGURATION.library_addr2,
        'zip': GENERAL_CONFIGURATION.library_zip,
        'city': GENERAL_CONFIGURATION.library_city,
        'phone_number': GENERAL_CONFIGURATION.library_phone_number,
        'email': GENERAL_CONFIGURATION.library_email,
        'website': GENERAL_CONFIGURATION.library_website,
    }
except OperationalError:
    # To prevent "django.db.utils.OperationalError" when reseting the DB
    pass
