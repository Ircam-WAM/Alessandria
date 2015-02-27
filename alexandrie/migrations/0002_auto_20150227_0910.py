# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alexandrie', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='isbnimport',
            name='source',
        ),
        migrations.DeleteModel(
            name='IsbnImportSource',
        ),
        migrations.RemoveField(
            model_name='author',
            name='import_source',
        ),
        migrations.RemoveField(
            model_name='publisher',
            name='import_source',
        ),
        migrations.DeleteModel(
            name='IsbnImport',
        ),
    ]
