#-*- encoding:utf-8 *-*

"""Filter used in html files (e.g. book_detail.html)"""

from django import template
register = template.Library()

@register.filter(name='addcss')
def addcss(field, css):
    return field.as_widget(attrs={"class":css})
