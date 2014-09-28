#-*- encoding:utf-8 *-*
from django.db import models
from django.contrib.auth.models import User as DjangoUser
from django.core.urlresolvers import reverse
from django_countries.fields import CountryField

class GeneralConfiguration(models.Model):
    max_borrow_days = models.PositiveSmallIntegerField(u"Nombre de jours maximum pour le prêt")
    
    class Meta:
        verbose_name = u"Configuration générale"
        verbose_name_plural = u"Configuration générale"

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
    return Language.objects.filter(is_default=True)[0]


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

#########
# Model #
#########

class ModelEntity(models.Model):
    notes = models.TextField(u"Notes", null=True, blank=True)    
    
    class Meta:
        abstract = True


class Reader(ModelEntity):
    number = models.CharField(u"Numéro", max_length=20, unique=True)
    first_name = models.CharField(u"Prénom", max_length=20)
    last_name = models.CharField(u"Nom", max_length=30)
    addr1 = models.CharField(u"Adresse 1", max_length=30)
    addr2 = models.CharField(u"Adresse 2", null=True, max_length=30, blank=True)
    zip = models.PositiveIntegerField(u"Code postal", max_length=5, null=True, blank=True)
    city = models.CharField(u"Ville", max_length=30)
    country = CountryField()
    inscription_date = models.DateField(u"Date d'inscription")
    email = models.EmailField(u"E-mail", unique=True, null=True, blank=True)
    phone_number = models.CharField(u"Téléphone", max_length=20, null=True, blank=True)
    profession = models.ForeignKey(Profession, null=True)

    def __str__(self):
        return "%s - %s %s" % (self.number, self.first_name, self.last_name)
    
    class Meta:
        verbose_name = "Lecteur"
    

class Author(ModelEntity):
    first_name = models.CharField(u"Prénom", max_length=20)
    last_name = models.CharField(u"Nom", max_length=30)
    birth_year = models.PositiveIntegerField(u"Année de naissance", max_length=4, null=True, blank=True)
    country = CountryField()

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)
        
    class Meta:
        verbose_name = "Auteur"


class Publisher(ModelEntity):
    name = models.CharField(u"Nom", max_length=30)
    country = CountryField()
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Editeur"


class Book(ModelEntity):
    title = models.CharField(u"Titre", max_length=50)
    authors = models.ManyToManyField(Author)
    publisher = models.ForeignKey(Publisher)
    classif_mark = models.CharField(u"Cote", max_length=10)
    height = models.PositiveIntegerField(u"Hauteur (mm)", max_length=3)
    isbn_nb = models.CharField(u"No. ISBN", max_length=30, null=True, blank=True)
    audience = models.ForeignKey(BookAudience)
    category = models.ForeignKey(BookCategory)
    sub_category = models.ForeignKey(BookSubCategory, null=True)
    price = models.FloatField('Prix', blank=True, null=True)
    language = models.ForeignKey(Language, default=get_default_language)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Livre"


class BookCopy(ModelEntity):
    number = models.CharField(u"Numéro", max_length=25)
    registered_on = models.DateField(u"Date d'enregistrement")
    book = models.ForeignKey(Book)
    condition = models.ForeignKey(BookCondition)
    is_bought = models.BooleanField(u"Acheté ?", null=False, blank=False, default=None)

    def __str(self):
        return "%s (%s)" %(self.book, self.number)

    class Meta:
        verbose_name = "Exemplaire d'un livre"
        verbose_name_plural = "Exemplaires d'un livre"


class ReaderBorrow(models.Model):
    reader = models.ForeignKey(Reader)
    bookCopy = models.ForeignKey(BookCopy)
    borrowed_date = models.DateField(u"Prêté le")
    borrow_due_date = models.DateField(u"Retour pour le")
    returned_on = models.DateField(u"Retourné le")
