#-*- encoding:utf-8 *-*

"""Filter used in html files (e.g. book_detail.html)"""

import ast
from django import template
register = template.Library()


@register.filter(name='addcss')
def addcss(field, css):
    field.field.widget.attrs.update({"class":css})
    return field.as_widget(attrs=field.field.widget.attrs)


@register.filter(name='htmlattributes')
def htmlattributes(field, attrs_dict):
    attr_dict = ast.literal_eval((attrs_dict))
    field.field.widget.attrs.update(attr_dict)
    return field.as_widget(attrs=field.field.widget.attrs)


@register.filter
def get_vars(object):
    return vars(object)