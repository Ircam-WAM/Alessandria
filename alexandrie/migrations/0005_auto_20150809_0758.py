# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alexandrie', '0004_auto_20150807_0629'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='height',
            field=models.PositiveIntegerField(verbose_name='Hauteur (cm)', blank=True, null=True),
        ),
    ]
