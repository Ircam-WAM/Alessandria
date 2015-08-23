#-*- encoding:utf-8 *-*

import isbnlib
from datetime import datetime as stddatetime
from datetime import datetime as stddate
from datetime import date as stddate

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User as DjangoUser
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django_countries.fields import CountryField

from alexandrie.utils import MyString, IsbnUtils


class GeneralConfiguration(models.Model):
    appli_name = models.TextField(verbose_name=u"Nom de l'application", default=u"Alexandrie")
    default_country = CountryField(verbose_name=u'Pays par défaut', default="FR")
    max_borrow_days = models.PositiveSmallIntegerField(u"Nombre de jours maximum pour le prêt", default=21)
    nav_history = models.PositiveSmallIntegerField(u"Historique de navigation", default=10)
    library_name = models.CharField(u"Nom bibliothèque", max_length=80)
    library_addr1 = models.CharField(u"Adresse 1 bibliothèque", max_length=30)
    library_addr2 = models.CharField(u"Adresse 2 bibliothèque", max_length=30, null=True, blank=True)
    library_zip = models.CharField(u"Code postal bibliothèque", max_length=10)
    library_city = models.CharField(u"Ville bibliothèque", max_length=30)
    library_country = CountryField(verbose_name=u'Pays bibliothèque')
    library_phone_number = models.CharField(u"Téléphone bibliothèque", max_length=20, null=True, blank=True)
    library_email = models.EmailField(u"E-mail bibliothèque", unique=True, null=True, blank=True)
    library_website = models.URLField(verbose_name='Site web bibliothèque', null=True, blank=True)

    @staticmethod
    def get():
        if GeneralConfiguration.objects.count() > 0:
            return GeneralConfiguration.objects.all()[0]
        else:
            gc = GeneralConfiguration()
            gc.save()
            return gc

    def __str__(self):
        return "Configuration"

    class Meta:
        verbose_name = u"Configuration générale de l'application"
        verbose_name_plural = u"Configuration générale de l'application"


class UserNavigationHistoryQuerySet(models.QuerySet):
    def get_list(self, user):
        return self.filter(accessed_by=user).order_by('accessed_by')

class UserNavigationHistory(models.Model):
    NAV_HISTORY = 10

    accessed_by = models.ForeignKey(DjangoUser)
    accessed_on = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=80)
    url = models.CharField(max_length=255)

    objects = UserNavigationHistoryQuerySet.as_manager()

    @staticmethod
    def add(url, title, user):
        lst = UserNavigationHistory.objects.get_list(user)
        if len(lst) >= UserNavigationHistory.NAV_HISTORY:
            lst[0].delete()
        h = UserNavigationHistory(url=url, title=title, accessed_by=user)
        h.save()

    @staticmethod
    def exist_url(url):
        return UserNavigationHistory.objects.filter(url=url).count() > 0

#############
# Reference #
#############

class ReferenceEntity(models.Model):
    label = models.CharField(u"Description", max_length=30)
    
    class Meta:
        abstract = True

    def __str__(self):
        return self.label


class Language(ReferenceEntity):
    #code = models.CharField(u"Code", max_length=5) # Internationalization https://docs.djangoproject.com/en/1.7/topics/i18n/
    is_default = models.BooleanField(u"Langue par défaut", default=False)

    class Meta:
        verbose_name = "Langue"

    @staticmethod
    def get_default_language():
        if Language.objects.count() > 0:
            return Language.objects.filter(is_default=True)[0]
        else:
            return None


class Profession(ReferenceEntity):
    class Meta:
        verbose_name = u"Profession"


class BookAudience(ReferenceEntity):
    class Meta:
        verbose_name = u"Public cible"
        verbose_name_plural = u"Publics cible"


class BookCondition(ReferenceEntity):
    class Meta:
        verbose_name = u"Etat d'un livre"
        verbose_name_plural = u"Etats d'un livre"


class BookCategory(ReferenceEntity):
    # For example : roman, documentaire, magazine, bd
    class Meta:
        verbose_name = u"Catégorie du livre"
        verbose_name_plural = u"Catégories d'un livre"


class BookSubCategory(ReferenceEntity):
    # For example : histoire / géographie (=> documentaire, magazine), policier / aventure (roman)
    parent_category = models.ForeignKey(BookCategory)
    class Meta:
        verbose_name = u"Sous-catégorie d'un livre"
        verbose_name_plural = u"Sous-catégories d'un livre"


class BookTag(ReferenceEntity):
    class Meta:
        verbose_name = u"Etiquette d'un livre"
        verbose_name_plural = u"Etiquettes d'un livre"


class BookCopyOrigin(ReferenceEntity):
    class Meta:
        verbose_name = u"Origine d'un livre"
        verbose_name_plural = u"Origines d'un livre"

#########
# Model #
#########

class ModelEntity(models.Model):
    created_by = models.ForeignKey(DjangoUser, related_name="%(app_label)s_%(class)s_add")
    created_on = models.DateTimeField(verbose_name=u"Créé le", auto_now_add=True)
    modified_by = models.ForeignKey(DjangoUser, related_name="%(app_label)s_%(class)s_update", null=True, blank=True)
    modified_on = models.DateTimeField(verbose_name=u"Modifié le", auto_now=True, null=True, blank=True)

    def clean(self, *args, **kwargs):
        super(ModelEntity, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        super(ModelEntity, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class AppliNewsQuerySet(models.QuerySet):
    def list(self):
        return self.filter(publish_date__lte=stddate.today())

    def get_last(self):
        # We use first, because of the default ordering
        return self.filter(publish_date__lte=stddate.today()).first()

class AppliNews(models.Model):
    publish_date = models.DateField(verbose_name=u"Date de publication")
    news = models.TextField(verbose_name=u"Info")

    objects = AppliNewsQuerySet.as_manager()

    def __str__(self):
        return "%s - %s" % (self.publish_date, self.news)

    class Meta:
        verbose_name = u"Info de l'application"
        verbose_name_plural = u"Infos de l'application"
        ordering = ['-publish_date']


class ReaderQuerySet(models.QuerySet):
    def get_by_first_and_last_name(self, first_name, last_name):
        return self.filter(
            first_name=first_name.title(),
            last_name=last_name.upper()
        ).first()

    def search(self, last_name=''):
        r_list = self.all()
        if last_name != '':
            r_list = r_list.filter(last_name__istartswith = last_name.upper())
        return r_list

class Reader(ModelEntity):
    number = models.PositiveIntegerField(u"Numéro", unique=True)
    inscription_date = models.DateField(u"Date d'inscription")
    first_name = models.CharField(u"Prénom", max_length=20)
    last_name = models.CharField(u"Nom", max_length=30)
    sex = models.CharField(u"Sexe", max_length=3, choices = (
                                                    ('f', u'Féminin'), 
                                                    ('m', u'Masculin'), 
                                                  )
    )
    birthday = models.DateField(u"Date de naissance")
    addr1 = models.CharField(u"Adresse 1", max_length=30)
    addr2 = models.CharField(u"Adresse 2", null=True, max_length=30, blank=True)
    zip = models.CharField(u"Code postal", max_length=10)
    city = models.CharField(u"Ville", max_length=30)
    country = CountryField(verbose_name=u'Pays')
    email = models.EmailField(u"E-mail", unique=True, null=True, blank=True)
    phone_number = models.CharField(u"Téléphone", max_length=20, null=True, blank=True)
    profession = models.ForeignKey(Profession, null=True, blank=True)
    disabled_on = models.DateField("Date de désactivation", blank=True, null=True)
    notes = models.TextField(u"Notes", null=True, blank=True)

    objects = ReaderQuerySet.as_manager()

    #Overriding
    def save(self, *args, **kwargs):
        if not self.pk:
            # Create mode => automatically generate a reader number
            self.number = Reader.objects.count() + 1
        super(Reader, self).save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        self.last_name = self.last_name.strip().upper()
        self.first_name = self.first_name.strip().title()
        if not self.email: # Force empty string to be 'None'
            self.email = None
        super(Reader, self).clean(*args, **kwargs)

    def is_disabled(self):
        return self.disabled_on is not None
    
    def list_borrow_all(self):
        return self.readerborrow_set.all()

    def list_borrow_current(self):
        return self.readerborrow_set.filter(returned_on=None)

    def list_borrow_late(self):
        return self.readerborrow_set.filter(returned_on=None, borrow_due_date__lt=stddatetime.now())
    
    def nb_borrow(self):
        return self.readerborrow_set.count()

    def get_full_name(self):
        if not self.first_name:
            return None
        return ' '.join([self.first_name, self.last_name])

    def get_absolute_url(self):
        return reverse('alexandrie:reader_update', kwargs={'pk': self.pk})

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)
    
    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = "Lecteur"

class AuthorQuerySet(models.QuerySet):
    def get_by_first_and_last_name(self, first_name, last_name):
        return self.filter(
            first_name=first_name.title(),
            last_name=last_name.upper(),
        ).first()

    def search(self, name=''):
        r_list = self.all()
        if name != '':
            r_list = r_list.filter(Q(last_name__istartswith = name) | Q(alias__istartswith = name))
        return r_list

class Author(ModelEntity):
    first_name = models.CharField(u"Prénom", max_length=20)
    last_name = models.CharField(u"Nom", max_length=30)
    alias = models.CharField(u"Nom d'emprunt", max_length=20, null=True, blank=True)
    birthday = models.DateField(u"Date de naissance", null=True, blank=True)
    country = CountryField(verbose_name=u'Pays')
    website = models.URLField(verbose_name='Site web', null=True, blank=True)
    notes = models.TextField(u"Notes", null=True, blank=True)
    is_isbn_import = models.BooleanField(u"Importé ISBN", default=False)

    objects = AuthorQuerySet.as_manager()

    def clean(self, *args, **kwargs):
        homonyms = Author.objects.filter(first_name__iexact=self.first_name
            ).filter(last_name__iexact=self.last_name
            ).filter(birthday=self.birthday
        )
        if len(homonyms) > 0:
            raise ValidationError({'last_name': u"Cet auteur existe déjà."})
        self.last_name = self.last_name.strip().upper()
        self.first_name = self.first_name.strip().title()
        if self.alias:
            self.alias = self.alias.strip().title()
        super(Author, self).clean(*args, **kwargs)

    def get_full_name(self):
        if not self.first_name:
            return ""
        full_name = ' '.join([self.first_name, self.last_name])
        if self.alias:
            full_name += ' (' + self.alias + ')'
        return full_name

    def get_books(self):
        return self.book_set.all()

    @staticmethod
    def init_from_isbn(isbn_meta):
        authors = []
        for author in isbn_meta['Authors']:
            # Example of author : "John Doe", "John Henry Doe"
            first_name, last_name = IsbnUtils.author_unpack(author)
            author = Author.objects.get_by_first_and_last_name(first_name, last_name)
            if author is None:
                author = Author(
                    first_name=first_name,
                    last_name=last_name,
                    country=IsbnUtils.get_country_code(isbn_meta)
                )
            authors.append(author)
        return authors

    def get_absolute_url(self):
        return reverse('alexandrie:author_update', kwargs={'pk': self.pk})

    def __str__(self):
        return self.get_full_name()

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = "Auteur"


class PublisherQuerySet(models.QuerySet):
    def get_by_name(self, name):
        return self.filter(name=name.upper()).first()

    def search(self, name=''):
        r_list = self.all()
        if name != '':
            r_list = r_list.filter(name__icontains = name.upper())
        return r_list

class Publisher(ModelEntity):
    name = models.CharField(u"Nom", max_length=30, unique=True)
    country = CountryField(verbose_name=u'Pays')
    notes = models.TextField(u"Notes", null=True, blank=True)
    is_isbn_import = models.BooleanField(u"Importé ISBN", default=False)

    objects = PublisherQuerySet.as_manager()

    def clean(self, *args, **kwargs):
        self.name = self.name.strip().upper()
        super(Publisher, self).clean(*args, **kwargs)

    @staticmethod
    def init_from_isbn(isbn_meta):
        name = isbn_meta['Publisher'].strip() if isbn_meta['Publisher'] else ""
        publisher = Publisher.objects.get_by_name(name)
        if publisher is None:
            publisher = Publisher(
                name=name,
                country=IsbnUtils.get_country_code(isbn_meta)
            )
        return publisher

    def get_absolute_url(self):
        return reverse('alexandrie:publisher_update', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = "Editeur"


class BookQuerySet(models.QuerySet):
    def get_by_title(self, title):
        return self.filter(name=name.capitalize()).first()

    def search(self, isbn_nb='', title='', category='', sub_category='', author_name=''):
        r_list = self.all()
        if (isbn_nb != ''):
            isbn_nb = isbnlib.get_canonical_isbn(isbn_nb)
            r_list = r_list.filter(isbn_nb = isbn_nb)
        if (title != ''):
            r_list = r_list.filter(title__icontains = title)
        if (category != ''):
            r_list = r_list.filter(category__id = category)
        if (sub_category != ''):
            r_list = r_list.filter(sub_category__id = sub_category)
        if (author_name != ''):
            r_list = r_list.filter(Q(authors__last_name__icontains=author_name) | Q(authors__alias__icontains=author_name))
        return r_list

class Book(ModelEntity):
    title = models.CharField(u"Titre", max_length=50)
    authors = models.ManyToManyField(Author, verbose_name=u'Auteurs')
    publishers = models.ManyToManyField(Publisher, verbose_name=u'Editeurs')
    publish_date = models.DateField(u"Date d'édition")
    edition_name = models.CharField(u"Titre édition", max_length=80, null=True, blank=True)
    classif_mark = models.CharField(u"Cote", max_length=10)
    height = models.PositiveIntegerField(u"Hauteur (cm)", null=True, blank=True)
    isbn_nb = models.CharField(u"No. ISBN", max_length=20, null=True, blank=True, unique=True)
    audiences = models.ManyToManyField(BookAudience, verbose_name=u'Public cible')
    category = models.ForeignKey(BookCategory, verbose_name=u'Catégorie')
    sub_category = models.ForeignKey(BookSubCategory, null=True, blank=True, verbose_name=u'Sous-catégorie')
    abstract = models.TextField(u"Résumé", null=True, blank=True)
    tags = models.ManyToManyField(BookTag, verbose_name=u'Etiquettes', blank=True)
    language = models.ForeignKey(Language, verbose_name=u'Langue')
    cover_pic = models.ImageField(verbose_name=u'Couverture', upload_to='alexandrie/upload', null=True, blank=True)
    related_to = models.ForeignKey('Book', null=True, blank=True, verbose_name=u"Apparenté à")
    notes = models.TextField(u"Notes", null=True, blank=True)
    is_isbn_import = models.BooleanField(u"Import ISBN", default=False)

    objects = BookQuerySet.as_manager()

    def clean(self, *args, **kwargs):
        if not self.isbn_nb: # Force empty string to be 'None'
            self.isbn_nb = None
        else:
            self.isbn_nb = isbnlib.get_canonical_isbn(self.isbn_nb)
            if not self.isbn_nb:
                raise ValidationError({'isbn_nb': u"No. ISBN invalide"})
        self.title = self.title.strip().capitalize()
        super(Book, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Book, self).save(*args, **kwargs)

    @staticmethod
    def init_from_isbn(isbn_meta):
        book = None
        if isbn_meta:
            book = Book()
            book.title = isbn_meta['Title'].strip()
            book.isbn_nb = isbn_meta['ISBN-13'] if isbn_meta.get('ISBN-13') else isbn_meta['ISBN-10']
            #language_code = isbn_meta['Language'][:2].upper()
            #self.language = isbn_meta['Language'][:2].upper()
            if isbn_meta['Year']:
                book.publish_date = stddate(year=int(isbn_meta['Year']), month=1, day=1)
            r_book = Book.objects.filter(isbn_nb=book.isbn_nb).first()
            if r_book:
                # The book already exists in the database
                book.id = r_book.id
        return book

    def get_nb_copy(self):
        return self.bookcopy_set.count()
    get_nb_copy.short_description = 'Nb exemplaires'
    
    def has_copies(self):
        return self.get_nb_copy() > 0

    def get_absolute_url(self):
        return reverse('alexandrie:book_update', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_on']
        verbose_name = "Livre"


class BookCopy(ModelEntity):
    number = models.PositiveIntegerField(u"Numéro")
    registered_on = models.DateField(u"Date d'enregistrement")
    book = models.ForeignKey(Book, verbose_name=u"Livre")
    condition = models.ForeignKey(BookCondition, verbose_name=u"Etat")
    origin = models.ForeignKey(BookCopyOrigin, verbose_name=u"Origine")
    price = models.FloatField("Prix", blank=True, null=True)
    price_date = models.DateField("Date (prix)", blank=True, null=True)
    disabled_on = models.DateField("Date de retrait", blank=True, null=True)
    notes = models.TextField(u"Notes", null=True, blank=True)

    #Overriding
    def save(self, *args, **kwargs):
        if not self.pk:
            # Create mode => automatically generate a book copy number
            self.number = BookCopy.objects.filter(book__id=self.book.id).count() + 1
        super(BookCopy, self).save(*args, **kwargs)

    def was_borrowed(self):
        return self.readerborrow_set.count() > 0

    def is_disabled(self):
        return self.disabled_on is not None

    def disabled_on_label(self): # Convenient function to be accessed from the template
        return self._meta.get_field('disabled_on').verbose_name

    def __str__(self):
        return "%s (%s)" %(str(self.book), self.number)

    class Meta:
        ordering = ['number']
        verbose_name = "Exemplaire d'un livre"
        verbose_name_plural = "Exemplaires d'un livre"


class ReaderBorrowQuerySet(models.QuerySet):
    def list_all_by_book(self, book_id):
        return self.filter(bookcopy__book__id=book_id)

    def list_current(self):
        return self.filter(returned_on=None)

    def list_late(self):
        return self.filter(returned_on=None, borrow_due_date__lt=stddatetime.now())

class ReaderBorrow(ModelEntity):
    reader = models.ForeignKey(Reader, verbose_name=u'Lecteur')
    bookcopy = models.ForeignKey(BookCopy, verbose_name=u'Exemplaire')
    borrowed_date = models.DateField(u"Prêté le")
    borrow_due_date = models.DateField(u"Retour pour le")
    returned_on = models.DateField(u"Retourné le", blank=True, null=True)
    notes = models.TextField(u"Notes", null=True, blank=True)

    objects = ReaderBorrowQuerySet.as_manager()

    def clean(self):
        already_borrowed = ReaderBorrow.objects.filter(
            bookcopy__id=self.bookcopy.id
        ).filter(
            returned_on=None
        ).first()
        error = False
        if already_borrowed is not None:
            if self.id: # Update mode
                if already_borrowed.id != self.id: # Not updating the current record
                    error = True
            else: # Create mode
                error = True
            if error:
                raise ValidationError(
                    {'bookcopy': u"Cet exemplaire a été déjà emprunté par %s %s"
                                 % (already_borrowed.reader.first_name, already_borrowed.reader.last_name)}
                )

    def is_returned(self):
        return self.returned_on is not None

    def is_returned_str(self):
        return "Oui" if self.returned_on is not None else "Non"

    def is_late(self):
        return self.borrow_due_date < stddate.today()

    def list_all():
        return ReaderBorrow.objects.all()

    def get_full_name(self):
        if self.borrowed_date:
            return "Emprunt du %s" % self.borrowed_date
        return None

    def get_absolute_url(self):
        return reverse('alexandrie:reader_borrow_update', kwargs={'pk': self.pk})

    def __str__(self):
        return "%s : %s" %(str(self.reader), str(self.bookcopy.book))

    class Meta:
        ordering = ['borrow_due_date']
        verbose_name = "Emprunt lecteur"
