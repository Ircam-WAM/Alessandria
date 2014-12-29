# -*- coding: utf-8 -*-

from django.conf import settings # import the settings file

def js_datepicker_lang(request):
    return {'JS_DATEPICKER_LANG': settings.LANGUAGE_CODE[:2]}