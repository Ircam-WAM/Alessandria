from fpdf import FPDF
from django.http import HttpResponse
from django.contrib import admin
from alessandria.models import (
    GeneralConfiguration, Language, Profession, BookCondition, BookCategory, BookSubCategory, BookAudience, BookTag,
    BookCopyOrigin, AppliNews, Book
)


class LanguageAdmin(admin.ModelAdmin):
    list_display = ('is_default', 'label')


def print_qrcode(modeladmin, request, queryset):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="somefilename.pdf"'
    pdf = FPDF("P", "mm", "A4")
    pdf.set_font("Courier", '', 10)
    pdf.set_text_color(255, 255, 255)
    pdf.add_page()
    pdf.cell(40, 10, 'Hello World!')
    output = pdf.output("yourfile.pdf", "S")
    response.write(output)
    return response

print_qrcode.short_description = "Print QRCode of selected objects"

class BookAdmin(admin.ModelAdmin):
    actions = [print_qrcode]


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
admin.site.register(Book, BookAdmin)

