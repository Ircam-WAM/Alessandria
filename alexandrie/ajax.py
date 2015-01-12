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
    category_id = int(request.POST['category_id'])
    data = []
    if category_id:
        sub_categories = BookSubCategory.objects.filter(parent_category=category_id)
        for sub_category in sub_categories:
            data.append({'id': sub_category.id, 'name': sub_category.label})
        response = {'item_list':data}
    return HttpResponse(simplejson.dumps(response))