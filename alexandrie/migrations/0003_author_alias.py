# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alexandrie', '0002_auto_20150801_1710'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='alias',
            field=models.CharField(blank=True, verbose_name="Nom d'emprunt", max_length=20, null=True),
        ),
    ]
