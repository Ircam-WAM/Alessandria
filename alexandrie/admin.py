from django.contrib import admin
from alexandrie.models import *

class LanguageAdmin(admin.ModelAdmin):
    list_display = ('is_default', 'label')

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_nb_copy')

admin.site.register(GeneralConfiguration)
admin.site.register(Language, LanguageAdmin)
admin.site.register(Profession)
admin.site.register(BookCondition)
admin.site.register(BookCategory)
admin.site.register(BookSubCategory)
admin.site.register(BookAudience)

admin.site.register(Reader)
admin.site.register(Book, BookAdmin)
admin.site.register(BookCopy)
admin.site.register(Author)
admin.site.register(Publisher)
