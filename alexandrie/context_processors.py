# -*- coding: utf-8 -*-
from django.conf import settings

def js_datepicker_lang(request):
    return {'JS_DATEPICKER_LANG': settings.LANGUAGE_CODE[:2]}

def app_version(request):
    from alexandrie import __version__ # read from __init__.py file
    return {'VERSION': __version__}

def library_infos(request):
    return {'LIBRARY_NAME': settings.LIBRARY_INFOS['name']}
