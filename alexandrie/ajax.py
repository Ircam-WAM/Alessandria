# -*- coding: utf-8 -*-
"""
Various Ajax stuff
"""

import simplejson
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from alexandrie.models import BookCategory, BookSubCategory

@csrf_exempt
def get_book_sub_categories(request):
    response = {}
    data = []
    if request.POST['category_id']:
        sub_categories = BookSubCategory.objects.filter(parent_category=int(request.POST['category_id']))
        for sub_category in sub_categories:
            data.append({'id': sub_category.id, 'name': sub_category.label})
        response = {'item_list':data}
    return HttpResponse(simplejson.dumps(response))
