#-*- encoding:utf-8 *-*

from datetime import datetime as stddatetime
from datetime import date as stddate

from django.db import models
from django.contrib.auth.models import User as DjangoUser
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django_countries.fields import CountryField


class GeneralConfiguration(models.Model):
    default_country = CountryField(verbose_name=u'Pays par défaut', default="FR")
    max_borrow_days = models.PositiveSmallIntegerField(u"Nombre de jours maximum pour le prêt", default=21)
    nav_history = models.PositiveSmallIntegerField(u"Historique de navigation", default=10)

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


class UserNavigationHistory(models.Model):
    NAV_HISTORY = 10

    accessed_by = models.ForeignKey(DjangoUser)
    accessed_on = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=80)
    url = models.CharField(max_length=255)

    @staticmethod
    def add(url, title, user):
        lst = UserNavigationHistory.get_list(user)
        if len(lst) >= UserNavigationHistory.NAV_HISTORY:
            lst[0].delete()
        h = UserNavigationHistory(url=url, title=title, accessed_by=user)
        h.save()

    @staticmethod
    def get_list(user):
        return UserNavigationHistory.objects.filter(accessed_by=user).order_by('accessed_by')

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


class IsbnImportSource(ReferenceEntity):
    code = models.CharField(u"Code", max_length=3)
    website = models.URLField(verbose_name=u"Site web")

    class Meta:
        verbose_name = u"Source pour l'importation ISBN"
        verbose_name_plural = u"Sources pour l'importation ISBN"


class IsbnImport(ReferenceEntity):
    entity_id = models.CharField(u"Identifiant", max_length=50)
    entity_type = models.CharField(u"type", max_length=20) # Example: Author, Book, Publisher
    source = models.ForeignKey(IsbnImportSource, verbose_name=u"Source")
    import_url = models.URLField(verbose_name=u"URL d'import")


#########
# Model #
#########

class ModelEntity(models.Model):
    created_by = models.ForeignKey(DjangoUser, related_name="%(app_label)s_%(class)s_add")
    created_on = models.DateTimeField(verbose_name=u"Créé le", auto_now_add=True)
    modified_by = models.ForeignKey(DjangoUser, related_name="%(app_label)s_%(class)s_update", null=True)
    modified_on = models.DateTimeField(verbose_name=u"Modifié le", auto_now=True, null=True)

    class Meta:
        abstract = True


class AppliNews(models.Model):
    publish_date = models.DateField(verbose_name=u"Date de publication")
    news = models.TextField(verbose_name=u"Info")

    @staticmethod
    def get_last():
        return AppliNews.objects.filter(publish_date__lte=stddate.today()).last()

    @staticmethod
    def list():
        return AppliNews.objects.filter(publish_date__lte=stddate.today())

    def __str__(self):
        return "%s - %s" % (self.publish_date, self.news)

    class Meta:
        verbose_name = u"Info de l'application"
        verbose_name_plural = u"Infos de l'application"


class Reader(ModelEntity):
    number = models.PositiveIntegerField(u"Numéro", unique=True)
    inscription_date = models.DateField(u"Date d'inscription")
    first_name = models.CharField(u"Prénom", max_length=20)
    last_name = models.CharField(u"Nom", max_length=30)
    sex = models.CharField(u"Sexe", max_length=3, choices = (
                                                    ('f', u'Femme'), 
                                                    ('m', u'Homme'), 
                                                  )
    )
    birthday = models.DateField(u"Date de naissance")
    addr1 = models.CharField(u"Adresse 1", max_length=30)
    addr2 = models.CharField(u"Adresse 2", null=True, max_length=30, blank=True)
    zip = models.PositiveIntegerField(u"Code postal", max_length=5)
    city = models.CharField(u"Ville", max_length=30)
    country = CountryField(verbose_name=u'Pays')
    email = models.EmailField(u"E-mail", unique=True, null=True, blank=True)
    phone_number = models.CharField(u"Téléphone", max_length=20, null=True, blank=True)
    profession = models.ForeignKey(Profession, null=True, blank=True)
    disabled_on = models.DateField("Date de désactivation", blank=True, null=True)
    notes = models.TextField(u"Notes", null=True, blank=True)

    #Overriding
    def save(self, *args, **kwargs):
        if not self.pk:
            # Create mode => automatically generate a reader number
            self.number = Reader.objects.count() + 1
        super(Reader, self).save(*args, **kwargs)

    def clean(self):
        if not self.email: # Force empty string to be 'None'
            self.email = None

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
        return "%s - %s %s" % (self.number, self.first_name, self.last_name)
    
    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = "Lecteur"


class Author(ModelEntity):
    first_name = models.CharField(u"Prénom", max_length=20)
    last_name = models.CharField(u"Nom", max_length=30)
    country = CountryField(verbose_name=u'Pays')
    website = models.URLField(verbose_name='Site web', null=True, blank=True)
    notes = models.TextField(u"Notes", null=True, blank=True)
    import_source = models.ForeignKey(IsbnImport, null=True, blank=True, verbose_name="Import")

    def get_full_name(self):
        if not self.first_name:
            return ""
        return ' '.join([self.first_name, self.last_name])

    def get_books(self):
        return self.book_set.all()

    def get_absolute_url(self):
        return reverse('alexandrie:author_update', kwargs={'pk': self.pk})

    def __str__(self):
        return self.get_full_name()

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = "Auteur"


class Publisher(ModelEntity):
    name = models.CharField(u"Nom", max_length=30, unique=True)
    country = CountryField(verbose_name=u'Pays')
    notes = models.TextField(u"Notes", null=True, blank=True)
    import_source = models.ForeignKey(IsbnImport, null=True, blank=True, verbose_name="Import")

    def get_absolute_url(self):
        return reverse('alexandrie:publisher_update', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = "Editeur"


class Book(ModelEntity):
    title = models.CharField(u"Titre", max_length=50)
    authors = models.ManyToManyField(Author, verbose_name=u'Auteurs')
    publishers = models.ManyToManyField(Publisher, verbose_name=u'Editeurs')
    publish_date = models.DateField(u"Date d'édition")
    edition_name = models.CharField(u"Titre édition", max_length=80, null=True, blank=True)
    classif_mark = models.CharField(u"Cote", max_length=10)
    height = models.PositiveIntegerField(u"Hauteur (cm)", max_length=3)
    isbn_nb = models.CharField(u"No. ISBN", max_length=20, null=True, blank=True, unique=True)
    audiences = models.ManyToManyField(BookAudience, verbose_name=u'Public cible')
    category = models.ForeignKey(BookCategory, verbose_name=u'Catégorie')
    sub_category = models.ForeignKey(BookSubCategory, null=True, verbose_name=u'Sous-catégorie')
    abstract = models.TextField(u"Résumé", null=True, blank=True)
    tags = models.ManyToManyField(BookTag, verbose_name=u'Etiquettes', null=True, blank=True)
    language = models.ForeignKey(Language, default=get_default_language, verbose_name=u'Langue')
    cover_pic = models.ImageField(verbose_name=u'Couverture', upload_to='alexandrie/upload', null=True, blank=True)
    related_to = models.ForeignKey('Book', null=True, blank=True, verbose_name=u"Apparenté à")
    notes = models.TextField(u"Notes", null=True, blank=True)

    def clean(self):
        self.isbn_nb = Book.strip_isbn(self.isbn_nb)
        if not self.isbn_nb: # Force empty string to be 'None'
            self.isbn_nb = None
        else:
            err_msg = Book.check_isbn_valid(self.isbn_nb)
            if len(err_msg) > 0:
                raise ValidationError({'isbn_nb': err_msg})

    def get_nb_copy(self):
        return self.bookcopy_set.count()
    get_nb_copy.short_description = 'Nb exemplaires'
    
    def has_copies(self):
        return self.get_nb_copy() > 0

    @staticmethod
    def strip_isbn(isbn_nb):
        return isbn_nb.replace('-', '')

    @staticmethod
    def check_isbn_valid(isbn_nb):
        raw_isbn = Book.strip_isbn(isbn_nb)
        if len(raw_isbn) > 0:
            if len(raw_isbn) != 10 and len(raw_isbn) != 13:
                return u"Le no. ISBN doit comporter 10 ou 13 chiffres"
            if len(raw_isbn) == 10:
                sum_pond = 0
                for i in range(0, len(raw_isbn)-1):
                    sum_pond = sum_pond + (i+1) * (int(raw_isbn[i]))
                checksum = 11 - (sum_pond % 11)
                if checksum != int(raw_isbn[-1:]):
                    return "ISBN 10: code de controle incorrect"
            elif len(raw_isbn) == 13:
                sum_pond = 0
                for i in range(0, 12, 2): # c0+c2+...+c10
                    sum_pond = sum_pond + int(raw_isbn[i])
                sum_pond2 = 0
                for i in range(1, 13, 2): # c1+c3+...+c11
                    sum_pond2 = sum_pond2 + int(raw_isbn[i])
                sum_pond2 = sum_pond2 *3
                sum_pond = sum_pond + sum_pond2
                if (sum_pond + int(raw_isbn[-1:])) % 10 != 0:
                    return "ISBN 13: code de controle incorrect"
        return ""

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
    is_bought = models.BooleanField(u"Acheté ?", null=False, blank=False, default=None)
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


class ReaderBorrow(ModelEntity):
    reader = models.ForeignKey(Reader, verbose_name=u'Lecteur')
    bookcopy = models.ForeignKey(BookCopy, verbose_name=u'Exemplaire')
    borrowed_date = models.DateField(u"Prêté le")
    borrow_due_date = models.DateField(u"Retour pour le")
    returned_on = models.DateField(u"Retourné le", blank=True, null=True)
    notes = models.TextField(u"Notes", null=True, blank=True)

    def is_returned(self):
        return self.returned_on is not None

    def is_returned_str(self):
        return "Oui" if self.returned_on is not None else "Non"

    def is_late(self):
        return self.borrow_due_date < stddate.today()

    def list_all():
        return ReaderBorrow.objects.all()

    @staticmethod
    def list_all_by_book(book_id):
        return ReaderBorrow.objects.filter(bookcopy__book__id=book_id)

    def list_current():
        return ReaderBorrow.objects.filter(returned_on=None)

    def list_late():
        return ReaderBorrow.objects.filter(returned_on=None, borrow_due_date__lt=stddatetime.now())

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