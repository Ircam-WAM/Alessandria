# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django_countries.fields


class Migration(migrations.Migration):

    replaces = [('alexandrie', '0001_initial'), ('alexandrie', '0002_auto_20150801_1710'), ('alexandrie', '0003_author_alias'), ('alexandrie', '0004_auto_20150807_0629'), ('alexandrie', '0005_auto_20150809_0758')]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AppliNews',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('publish_date', models.DateField(verbose_name='Date de publication')),
                ('news', models.TextField(verbose_name='Info')),
            ],
            options={
                'verbose_name': "Info de l'application",
                'ordering': ['-publish_date'],
                'verbose_name_plural': "Infos de l'application",
            },
        ),
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('created_on', models.DateTimeField(verbose_name='Créé le', auto_now_add=True)),
                ('modified_on', models.DateTimeField(verbose_name='Modifié le', null=True, auto_now=True)),
                ('first_name', models.CharField(verbose_name='Prénom', max_length=20)),
                ('last_name', models.CharField(verbose_name='Nom', max_length=30)),
                ('country', django_countries.fields.CountryField(verbose_name='Pays', max_length=2)),
                ('website', models.URLField(verbose_name='Site web', null=True, blank=True)),
                ('notes', models.TextField(verbose_name='Notes', null=True, blank=True)),
                ('is_isbn_import', models.BooleanField(verbose_name='Importé ISBN', default=False)),
                ('created_by', models.ForeignKey(related_name='alexandrie_author_add', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True, related_name='alexandrie_author_update')),
                ('birthday', models.DateField(verbose_name='Date de naissance', null=True, blank=True)),
                ('alias', models.CharField(max_length=20, verbose_name="Nom d'emprunt", null=True, blank=True)),
            ],
            options={
                'verbose_name': 'Auteur',
                'ordering': ['last_name', 'first_name'],
            },
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('created_on', models.DateTimeField(verbose_name='Créé le', auto_now_add=True)),
                ('modified_on', models.DateTimeField(verbose_name='Modifié le', null=True, auto_now=True)),
                ('title', models.CharField(verbose_name='Titre', max_length=50)),
                ('publish_date', models.DateField(verbose_name="Date d'édition")),
                ('edition_name', models.CharField(max_length=80, verbose_name='Titre édition', null=True, blank=True)),
                ('classif_mark', models.CharField(verbose_name='Cote', max_length=10)),
                ('height', models.PositiveIntegerField(verbose_name='Hauteur (cm)', max_length=3)),
                ('isbn_nb', models.CharField(max_length=20, unique=True, verbose_name='No. ISBN', null=True, blank=True)),
                ('abstract', models.TextField(verbose_name='Résumé', null=True, blank=True)),
                ('cover_pic', models.ImageField(upload_to='alexandrie/upload', verbose_name='Couverture', null=True, blank=True)),
                ('notes', models.TextField(verbose_name='Notes', null=True, blank=True)),
                ('is_isbn_import', models.BooleanField(verbose_name='Importé ISBN', default=False)),
            ],
            options={
                'verbose_name': 'Livre',
                'ordering': ['-created_on'],
            },
        ),
        migrations.CreateModel(
            name='BookAudience',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('label', models.CharField(verbose_name='Description', max_length=30)),
            ],
            options={
                'verbose_name': 'Public cible',
                'verbose_name_plural': 'Publics cible',
            },
        ),
        migrations.CreateModel(
            name='BookCategory',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('label', models.CharField(verbose_name='Description', max_length=30)),
            ],
            options={
                'verbose_name': 'Catégorie du livre',
                'verbose_name_plural': "Catégories d'un livre",
            },
        ),
        migrations.CreateModel(
            name='BookCondition',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('label', models.CharField(verbose_name='Description', max_length=30)),
            ],
            options={
                'verbose_name': "Etat d'un livre",
                'verbose_name_plural': "Etats d'un livre",
            },
        ),
        migrations.CreateModel(
            name='BookCopy',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('created_on', models.DateTimeField(verbose_name='Créé le', auto_now_add=True)),
                ('modified_on', models.DateTimeField(verbose_name='Modifié le', null=True, auto_now=True)),
                ('number', models.PositiveIntegerField(verbose_name='Numéro')),
                ('registered_on', models.DateField(verbose_name="Date d'enregistrement")),
                ('price', models.FloatField(verbose_name='Prix', null=True, blank=True)),
                ('price_date', models.DateField(verbose_name='Date (prix)', null=True, blank=True)),
                ('disabled_on', models.DateField(verbose_name='Date de retrait', null=True, blank=True)),
                ('notes', models.TextField(verbose_name='Notes', null=True, blank=True)),
                ('book', models.ForeignKey(verbose_name='Livre', to='alexandrie.Book')),
                ('condition', models.ForeignKey(verbose_name='Etat', to='alexandrie.BookCondition')),
                ('created_by', models.ForeignKey(related_name='alexandrie_bookcopy_add', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True, related_name='alexandrie_bookcopy_update')),
            ],
            options={
                'verbose_name': "Exemplaire d'un livre",
                'ordering': ['number'],
                'verbose_name_plural': "Exemplaires d'un livre",
            },
        ),
        migrations.CreateModel(
            name='BookCopyOrigin',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('label', models.CharField(verbose_name='Description', max_length=30)),
            ],
            options={
                'verbose_name': "Origine d'un livre",
                'verbose_name_plural': "Origines d'un livre",
            },
        ),
        migrations.CreateModel(
            name='BookSubCategory',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('label', models.CharField(verbose_name='Description', max_length=30)),
                ('parent_category', models.ForeignKey(to='alexandrie.BookCategory')),
            ],
            options={
                'verbose_name': "Sous-catégorie d'un livre",
                'verbose_name_plural': "Sous-catégories d'un livre",
            },
        ),
        migrations.CreateModel(
            name='BookTag',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('label', models.CharField(verbose_name='Description', max_length=30)),
            ],
            options={
                'verbose_name': "Etiquette d'un livre",
                'verbose_name_plural': "Etiquettes d'un livre",
            },
        ),
        migrations.CreateModel(
            name='GeneralConfiguration',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('appli_name', models.TextField(verbose_name="Nom de l'application", default='Alexandrie')),
                ('default_country', django_countries.fields.CountryField(verbose_name='Pays par défaut', default='FR', max_length=2)),
                ('max_borrow_days', models.PositiveSmallIntegerField(verbose_name='Nombre de jours maximum pour le prêt', default=21)),
                ('nav_history', models.PositiveSmallIntegerField(verbose_name='Historique de navigation', default=10)),
                ('library_addr1', models.CharField(verbose_name='Adresse 1 bibliothèque', default='Le Bourg', max_length=30)),
                ('library_addr2', models.CharField(max_length=30, verbose_name='Adresse 2 bibliothèque', null=True, blank=True)),
                ('library_city', models.CharField(verbose_name='Ville bibliothèque', default='La Genête', max_length=30)),
                ('library_country', django_countries.fields.CountryField(verbose_name='Pays bibliothèque', default='FR', max_length=2)),
                ('library_email', models.EmailField(max_length=254, unique=True, verbose_name='E-mail bibliothèque', null=True, blank=True)),
                ('library_name', models.CharField(verbose_name='Nom bibliothèque', default='Bibliothèque de La Genête', max_length=80)),
                ('library_phone_number', models.CharField(max_length=20, verbose_name='Téléphone bibliothèque', null=True, blank=True)),
                ('library_website', models.URLField(verbose_name='Site web bibliothèque', null=True, blank=True)),
                ('library_zip', models.CharField(verbose_name='Code postal bibliothèque', default=71290, max_length=10)),
            ],
            options={
                'verbose_name': "Configuration générale de l'application",
                'verbose_name_plural': "Configuration générale de l'application",
            },
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('label', models.CharField(verbose_name='Description', max_length=30)),
                ('is_default', models.BooleanField(verbose_name='Langue par défaut', default=False)),
            ],
            options={
                'verbose_name': 'Langue',
            },
        ),
        migrations.CreateModel(
            name='Profession',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('label', models.CharField(verbose_name='Description', max_length=30)),
            ],
            options={
                'verbose_name': 'Profession',
            },
        ),
        migrations.CreateModel(
            name='Publisher',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('created_on', models.DateTimeField(verbose_name='Créé le', auto_now_add=True)),
                ('modified_on', models.DateTimeField(verbose_name='Modifié le', null=True, auto_now=True)),
                ('name', models.CharField(verbose_name='Nom', unique=True, max_length=30)),
                ('country', django_countries.fields.CountryField(verbose_name='Pays', max_length=2)),
                ('notes', models.TextField(verbose_name='Notes', null=True, blank=True)),
                ('is_isbn_import', models.BooleanField(verbose_name='Importé ISBN', default=False)),
                ('created_by', models.ForeignKey(related_name='alexandrie_publisher_add', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True, related_name='alexandrie_publisher_update')),
            ],
            options={
                'verbose_name': 'Editeur',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Reader',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('created_on', models.DateTimeField(verbose_name='Créé le', auto_now_add=True)),
                ('modified_on', models.DateTimeField(verbose_name='Modifié le', null=True, auto_now=True)),
                ('number', models.PositiveIntegerField(verbose_name='Numéro', unique=True)),
                ('inscription_date', models.DateField(verbose_name="Date d'inscription")),
                ('first_name', models.CharField(verbose_name='Prénom', max_length=20)),
                ('last_name', models.CharField(verbose_name='Nom', max_length=30)),
                ('sex', models.CharField(choices=[('f', 'Féminin'), ('m', 'Masculin')], verbose_name='Sexe', max_length=3)),
                ('birthday', models.DateField(verbose_name='Date de naissance')),
                ('addr1', models.CharField(verbose_name='Adresse 1', max_length=30)),
                ('addr2', models.CharField(max_length=30, verbose_name='Adresse 2', null=True, blank=True)),
                ('zip', models.CharField(verbose_name='Code postal', max_length=10)),
                ('city', models.CharField(verbose_name='Ville', max_length=30)),
                ('country', django_countries.fields.CountryField(verbose_name='Pays', max_length=2)),
                ('email', models.EmailField(max_length=75, unique=True, verbose_name='E-mail', null=True, blank=True)),
                ('phone_number', models.CharField(max_length=20, verbose_name='Téléphone', null=True, blank=True)),
                ('disabled_on', models.DateField(verbose_name='Date de désactivation', null=True, blank=True)),
                ('notes', models.TextField(verbose_name='Notes', null=True, blank=True)),
                ('created_by', models.ForeignKey(related_name='alexandrie_reader_add', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True, related_name='alexandrie_reader_update')),
                ('profession', models.ForeignKey(blank=True, to='alexandrie.Profession', null=True)),
            ],
            options={
                'verbose_name': 'Lecteur',
                'ordering': ['last_name', 'first_name'],
            },
        ),
        migrations.CreateModel(
            name='ReaderBorrow',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('created_on', models.DateTimeField(verbose_name='Créé le', auto_now_add=True)),
                ('modified_on', models.DateTimeField(verbose_name='Modifié le', null=True, auto_now=True)),
                ('borrowed_date', models.DateField(verbose_name='Prêté le')),
                ('borrow_due_date', models.DateField(verbose_name='Retour pour le')),
                ('returned_on', models.DateField(verbose_name='Retourné le', null=True, blank=True)),
                ('notes', models.TextField(verbose_name='Notes', null=True, blank=True)),
                ('bookcopy', models.ForeignKey(verbose_name='Exemplaire', to='alexandrie.BookCopy')),
                ('created_by', models.ForeignKey(related_name='alexandrie_readerborrow_add', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True, related_name='alexandrie_readerborrow_update')),
                ('reader', models.ForeignKey(verbose_name='Lecteur', to='alexandrie.Reader')),
            ],
            options={
                'verbose_name': 'Emprunt lecteur',
                'ordering': ['borrow_due_date'],
            },
        ),
        migrations.CreateModel(
            name='UserNavigationHistory',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('accessed_on', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(max_length=80)),
                ('url', models.CharField(max_length=255)),
                ('accessed_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='bookcopy',
            name='origin',
            field=models.ForeignKey(verbose_name='Origine', to='alexandrie.BookCopyOrigin'),
        ),
        migrations.AddField(
            model_name='book',
            name='audiences',
            field=models.ManyToManyField(verbose_name='Public cible', to='alexandrie.BookAudience'),
        ),
        migrations.AddField(
            model_name='book',
            name='authors',
            field=models.ManyToManyField(verbose_name='Auteurs', to='alexandrie.Author'),
        ),
        migrations.AddField(
            model_name='book',
            name='category',
            field=models.ForeignKey(verbose_name='Catégorie', to='alexandrie.BookCategory'),
        ),
        migrations.AddField(
            model_name='book',
            name='created_by',
            field=models.ForeignKey(related_name='alexandrie_book_add', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='book',
            name='language',
            field=models.ForeignKey(verbose_name='Langue', to='alexandrie.Language'),
        ),
        migrations.AddField(
            model_name='book',
            name='modified_by',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True, related_name='alexandrie_book_update'),
        ),
        migrations.AddField(
            model_name='book',
            name='publishers',
            field=models.ManyToManyField(verbose_name='Editeurs', to='alexandrie.Publisher'),
        ),
        migrations.AddField(
            model_name='book',
            name='related_to',
            field=models.ForeignKey(verbose_name='Apparenté à', blank=True, to='alexandrie.Book', null=True),
        ),
        migrations.AddField(
            model_name='book',
            name='sub_category',
            field=models.ForeignKey(verbose_name='Sous-catégorie', blank=True, to='alexandrie.BookSubCategory', null=True),
        ),
        migrations.AddField(
            model_name='book',
            name='tags',
            field=models.ManyToManyField(verbose_name='Etiquettes', to='alexandrie.BookTag', blank=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='height',
            field=models.PositiveIntegerField(verbose_name='Hauteur (cm)'),
        ),
        migrations.AlterField(
            model_name='book',
            name='is_isbn_import',
            field=models.BooleanField(verbose_name='Import ISBN', default=False),
        ),
        migrations.AlterField(
            model_name='reader',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='E-mail', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='height',
            field=models.PositiveIntegerField(verbose_name='Hauteur (cm)', null=True, blank=True),
        ),
    ]
