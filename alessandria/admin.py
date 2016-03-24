# -*- coding: utf-8 -*-

from django.contrib import admin
from alessandria.models import *


class LanguageAdmin(admin.ModelAdmin):
    list_display = ('is_default', 'label')

admin.site.register(GeneralConfiguration)
admin.site.register(Language, LanguageAdmin)
admin.site.register(Profession)
admin.site.register(BookCondition)
admin.site.register(BookCategory)
admin.site.register(BookSubCategory)
admin.site.register(BookAudience)
admin.site.register(BookTag)
admin.site.register(BookCopyOrigin)
admin.site.register(AppliNews)
