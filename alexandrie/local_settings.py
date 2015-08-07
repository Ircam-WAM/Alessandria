# -*- coding: utf-8 -*-

"""
Django settings for the alexandrie app.
"""

from django.conf import global_settings
from django.db.utils import OperationalError

# define the lookup channels in use on the site (autocomplete stuff)
AJAX_LOOKUP_CHANNELS = {
    'reader_list': ('alexandrie.ajax_lookup', 'ReaderLookup'),
    'bookcopy_list': ('alexandrie.ajax_lookup', 'BookCopyLookup'),
    'author_list': ('alexandrie.ajax_lookup', 'AuthorLookup'),
    'publisher_list': ('alexandrie.ajax_lookup', 'PublisherLookup'),
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