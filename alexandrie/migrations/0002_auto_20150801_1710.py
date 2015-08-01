# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alexandrie', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='birthday',
            field=models.DateField(null=True, verbose_name='Date de naissance', blank=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='height',
            field=models.PositiveIntegerField(verbose_name='Hauteur (cm)'),
        ),
        migrations.AlterField(
            model_name='book',
            name='is_isbn_import',
            field=models.BooleanField(default=False, verbose_name='Import ISBN'),
        ),
        migrations.AlterField(
            model_name='book',
            name='tags',
            field=models.ManyToManyField(to='alexandrie.BookTag', verbose_name='Etiquettes', blank=True),
        ),
        migrations.AlterField(
            model_name='reader',
            name='email',
            field=models.EmailField(null=True, unique=True, max_length=254, verbose_name='E-mail', blank=True),
        ),
    ]
