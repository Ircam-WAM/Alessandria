from django.contrib import admin
from alexandrie.models import *

"""
class EntityAuditAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.added_by = request.user
        obj.updated_by = request.user
        obj.save()
"""

admin.site.register(GeneralConfiguration)
admin.site.register(Profession)
admin.site.register(BookCondition)
admin.site.register(BookCategory)
admin.site.register(BookSubCategory)
admin.site.register(BookAudience)

admin.site.register(Reader)
admin.site.register(Book)
admin.site.register(Author)
admin.site.register(Publisher)
