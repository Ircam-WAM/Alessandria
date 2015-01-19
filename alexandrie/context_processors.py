# -*- coding: utf-8 -*-
from django.conf import settings
from bibli._version import __version__

def js_datepicker_lang(request):
    return {'JS_DATEPICKER_LANG': settings.LANGUAGE_CODE[:2]}

def app_version(request):
    return {'VERSION': __version__}
