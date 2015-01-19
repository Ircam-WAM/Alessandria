# -*- coding: utf-8 -*-

"""
Django settings for the alexandrie app.
"""

from django.conf import global_settings
from django.db.utils import OperationalError

TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    # Used to access session attributes from the templates
    "django.core.context_processors.request",
    # Used for i18n of jquery date picker plugin (http://keith-wood.name/datepick.html)
    "alexandrie.context_processors.js_datepicker_lang",
    "alexandrie.context_processors.app_version",
)

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
except OperationalError:
    # To prevent "django.db.utils.OperationalError" when reseting the DB
    pass