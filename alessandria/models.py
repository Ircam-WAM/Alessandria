import isbnlib
import datetime

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User as DjangoUser
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django_countries.fields import CountryField

from alessandria.utils import IsbnUtils


class GeneralConfiguration(models.Model):
    appli_name = models.TextField(verbose_name=_("Software name"), default=u"Alessandria")
    default_country = CountryField(verbose_name=_("Default country"), default="FR")
    max_borrow_days = models.PositiveSmallIntegerField(_("Maximal borrowing days"), default=21)
    nav_history = models.PositiveSmallIntegerField(_("Navigation history"), default=10)
    library_name = models.CharField(_("Library name"), max_length=80)
    library_addr1 = models.CharField(_("Library address 1"), max_length=30)
    library_addr2 = models.CharField(_("Library address 2"), max_length=30, null=True, blank=True)
    library_zip = models.CharField(_("Library zip code"), max_length=10)
    library_city = models.CharField(_("Library city"), max_length=30)
    library_country = CountryField(verbose_name=_("Library country"))
    library_phone_number = models.CharField(_("Library phone"), max_length=20, null=True, blank=True)
    library_email = models.EmailField(_("Library e-mail"), unique=True, null=True, blank=True)
    library_website = models.URLField(verbose_name=_("Library website"), null=True, blank=True)

    def __str__(self):
        return ugettext("Configuration")  # TODO: check if it could be lazy

    class Meta:
        verbose_name = _("Global settings of the software")
        verbose_name_plural = verbose_name


class UserNavigationHistoryManager(models.Manager):
    def get_list(self, user):
        return self.filter(accessed_by=user).order_by('accessed_by')


class UserNavigationHistory(models.Model):
    NAV_HISTORY = 10

    accessed_by = models.ForeignKey(DjangoUser)
    accessed_on = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=80)
    url = models.CharField(max_length=255)

    objects = UserNavigationHistoryManager()

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
    # code = models.CharField(u"Code", max_length=5) # Internationalization https://docs.djangoproject.com/en/1.7/topics/i18n/
    is_default = models.BooleanField(_("Default language"), default=False)

    class Meta:
        verbose_name = _("Language")
        verbose_name_plural = _("Languages")

    @staticmethod
    def get_default_language():
        if Language.objects.count() > 0:
            return Language.objects.filter(is_default=True)[0]
        else:
            return None


class Profession(ReferenceEntity):
    class Meta:
        verbose_name = _("Job")
        verbose_name_plural = _("Jobs")


class BookAudience(ReferenceEntity):
    class Meta:
        verbose_name = _("Audience")
        verbose_name_plural = _("Audiences")


class BookCondition(ReferenceEntity):
    class Meta:
        verbose_name = _("Book condition")
        verbose_name_plural = _("Book conditions")


class BookCategory(ReferenceEntity):
    # For example : novel, documentary, magazine, cartoon
    class Meta:
        verbose_name = _("Book category")
        verbose_name_plural = _("Book categories")


class BookSubCategory(ReferenceEntity):
    # For example : history / geography (=> sub-category of documentary, magazine), detective / adventure (=> novel)
    parent_category = models.ForeignKey(BookCategory)

    class Meta:
        verbose_name = _("Book sub-category")
        verbose_name_plural = _("Book sub-categories")


class BookTag(ReferenceEntity):
    class Meta:
        verbose_name = _("Book tag")
        verbose_name_plural = _("Book tags")


class BookCopyOrigin(ReferenceEntity):
    class Meta:
        verbose_name = _("Book origin")
        verbose_name_plural = _("Book origins")

#########
# Model #
#########


class ModelEntity(models.Model):
    created_by = models.ForeignKey(DjangoUser, related_name="%(app_label)s_%(class)s_add")
    created_on = models.DateTimeField(verbose_name=u"Créé le", auto_now_add=True)
    modified_by = models.ForeignKey(DjangoUser, related_name="%(app_label)s_%(class)s_update", null=True, blank=True)
    modified_on = models.DateTimeField(verbose_name=u"Modifié le", auto_now=True, null=True, blank=True)

    def clean(self):
        super(ModelEntity, self).clean()

    def save(self, *args, **kwargs):
        super(ModelEntity, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class AppliNewsManager(models.Manager):
    def list(self):
        return self.filter(publish_date__lte=datetime.date.today())

    def get_last(self):
        # We use first, because of the default ordering
        return self.filter(publish_date__lte=datetime.date.today()).first()


class AppliNews(models.Model):
    publish_date = models.DateField(verbose_name=u"Date de publication")
    news = models.TextField(verbose_name=u"Info")

    objects = AppliNewsManager()

    def __str__(self):
        return "%s - %s" % (self.publish_date, self.news)

    class Meta:
        verbose_name = _("Software news (item)")
        verbose_name_plural = _("Software news")
        ordering = ['-publish_date']


class ReaderManager(models.Manager):
    def get_by_first_and_last_name(self, first_name, last_name):
        return self.filter(
            first_name=first_name.title(),
            last_name=last_name.upper()
        ).first()

    def search(self, last_name=''):
        r_list = self.all()
        if last_name != '':
            r_list = r_list.filter(last_name__istartswith=last_name)
        return r_list


class Reader(ModelEntity):
    number = models.PositiveIntegerField(_("Number"), unique=True)
    inscription_date = models.DateField(_("Registration date"))
    first_name = models.CharField(_("First name"), max_length=20)
    last_name = models.CharField(_("Last name"), max_length=30)
    sex = models.CharField(_("Gender"), max_length=3, choices=(('f', _("Female")), ('m', _("Male"))))
    birthday = models.DateField(_("Birthdate"))
    addr1 = models.CharField(_("Address 1"), max_length=30)
    addr2 = models.CharField(_("Address 2"), null=True, max_length=30, blank=True)
    zip = models.CharField(_("Zip code"), max_length=10)
    city = models.CharField(_("City"), max_length=30)
    country = CountryField(verbose_name=_("Country"))
    email = models.EmailField(_("E-mail"), unique=True, null=True, blank=True)
    phone_number = models.CharField(_("Phone"), max_length=20, null=True, blank=True)
    profession = models.ForeignKey(Profession, null=True, blank=True)
    disabled_on = models.DateField(_("Disabled on"), blank=True, null=True)
    notes = models.TextField(_("Notes"), null=True, blank=True)

    objects = ReaderManager()

    # Overriding
    def save(self, *args, **kwargs):
        if not self.pk:
            # Create mode => automatically generate a reader number
            self.number = Reader.objects.count() + 1
        super(Reader, self).save(*args, **kwargs)

    def clean(self):
        self.last_name = self.last_name.strip().upper()
        self.first_name = self.first_name.strip().title()
        if not self.email:  # Force empty string to be 'None'
            self.email = None
        super(Reader, self).clean()

    def is_disabled(self):
        return self.disabled_on is not None
    
    def list_borrow_all(self):
        return self.readerborrow_set.all()

    def list_borrow_current(self):
        return self.readerborrow_set.filter(returned_on=None)

    def list_borrow_late(self):
        return self.readerborrow_set.filter(returned_on=None, borrow_due_date__lt=datetime.datetime.now())
    
    def nb_borrow(self):
        return self.readerborrow_set.count()

    def get_full_name(self):
        if not self.first_name:
            return None
        return ' '.join([self.first_name, self.last_name])

    def get_absolute_url(self):
        return reverse('alessandria:reader_update', kwargs={'pk': self.pk})

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)
    
    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = _("Reader")
        verbose_name_plural = _("Readers")


class AuthorManager(models.Manager):
    def get_by_first_and_last_name(self, first_name, last_name):
        return self.filter(
            first_name=first_name.title(),
            last_name=last_name.upper(),
        ).first()

    def search(self, name=''):
        r_list = self.all()
        if name != '':
            r_list = r_list.filter(Q(last_name__istartswith=name) | Q(alias__istartswith=name))
        return r_list


class Author(ModelEntity):
    first_name = models.CharField(_("First name"), max_length=20)
    last_name = models.CharField(_("Last name"), max_length=30)
    alias = models.CharField(_("Alias"), max_length=20, null=True, blank=True)
    birthday = models.DateField(_("Birthdate"), null=True, blank=True)
    country = CountryField(verbose_name=_("Country"))
    website = models.URLField(verbose_name=_("Website"), null=True, blank=True)
    notes = models.TextField(_("Notes"), null=True, blank=True)
    is_isbn_import = models.BooleanField(_("ISBN import"), default=False)

    objects = AuthorManager()

    def clean(self):
        homonyms = Author.objects.filter(
            first_name__iexact=self.first_name
        ).filter(
            last_name__iexact=self.last_name
        ).filter(
            birthday=self.birthday
        ).exclude(
            id=self.id
        )
        if len(homonyms) > 0:
            raise ValidationError({'last_name': ugettext("This author already exists.")})
        self.last_name = self.last_name.strip().upper()
        self.first_name = self.first_name.strip().title()
        if self.alias:
            self.alias = self.alias.strip().title()
        super(Author, self).clean()

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
        return reverse('alessandria:author_update', kwargs={'pk': self.pk})

    def __str__(self):
        return self.get_full_name()

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = _("Author")
        verbose_name_plural = _("Authors")


class PublisherManager(models.Manager):
    def get_by_name(self, name):
        return self.filter(name=name.upper()).first()

    def search(self, name=''):
        r_list = self.all()
        if name != '':
            r_list = r_list.filter(name__icontains=name)
        return r_list


class Publisher(ModelEntity):
    name = models.CharField(_("Name"), max_length=30, unique=True)
    country = CountryField(verbose_name=_("Country"))
    notes = models.TextField(_("Notes"), null=True, blank=True)
    is_isbn_import = models.BooleanField(_("ISBN import"), default=False)

    objects = PublisherManager()

    def clean(self):
        self.name = self.name.strip().upper()
        super(Publisher, self).clean()

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
        return reverse('alessandria:publisher_update', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = "Publisher"
        verbose_name_plural = "Publishers"


class BookManager(models.Manager):
    def search(self, isbn_nb='', title='', category='', sub_category='', author_name=''):
        r_list = self.all()
        if isbn_nb != '':
            isbn_nb = isbnlib.get_canonical_isbn(isbn_nb)
            r_list = r_list.filter(isbn_nb=isbn_nb)
        if title != '':
            r_list = r_list.filter(title__icontains=title)
        if category != '':
            r_list = r_list.filter(category__id=category)
        if sub_category != '':
            r_list = r_list.filter(sub_category__id=sub_category)
        if author_name != '':
            r_list = (
                r_list.filter(Q(authors__last_name__icontains=author_name) | Q(authors__alias__icontains=author_name))
            )
        return r_list


class Book(ModelEntity):
    title = models.CharField(_("Title"), max_length=50)
    authors = models.ManyToManyField(Author, verbose_name=_("Authors"))
    publishers = models.ManyToManyField(Publisher, verbose_name=_("Publishers"))
    publish_date = models.DateField(_("Publishing date"))
    edition_name = models.CharField(_("Title edition"), max_length=80, null=True, blank=True)
    classif_mark = models.CharField(_("Classification mark"), max_length=10)
    height = models.PositiveIntegerField(_("Height (inches)"), null=True, blank=True)
    isbn_nb = models.CharField(_("ISBN number"), max_length=20, null=True, blank=True, unique=True)
    audiences = models.ManyToManyField(BookAudience, verbose_name=_("Audience"))
    category = models.ForeignKey(BookCategory, verbose_name=_("Category"))
    sub_category = models.ForeignKey(BookSubCategory, null=True, blank=True, verbose_name=_("Sub-category"))
    abstract = models.TextField(_("Abstract"), null=True, blank=True)
    tags = models.ManyToManyField(BookTag, verbose_name=_("Tags"), blank=True)
    language = models.ForeignKey(Language, verbose_name=_("Language"))
    cover_pic = models.ImageField(verbose_name=_("Cover"), upload_to='alessandria/upload', null=True, blank=True)
    related_to = models.ForeignKey('Book', null=True, blank=True, verbose_name=_("Linked to"))
    notes = models.TextField(_("Notes"), null=True, blank=True)
    is_isbn_import = models.BooleanField(_("ISBN import"), default=False)

    objects = BookManager()

    def clean(self):
        if not self.isbn_nb:  # Force empty string to be 'None'
            self.isbn_nb = None
        else:
            self.isbn_nb = isbnlib.get_canonical_isbn(self.isbn_nb)
            if not self.isbn_nb:
                raise ValidationError({'isbn_nb': ugettext("Invalid ISBN number.")})
        self.title = self.title.strip().capitalize()
        super(Book, self).clean()

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
            # language_code = isbn_meta['Language'][:2].upper()
            # self.language = isbn_meta['Language'][:2].upper()
            if isbn_meta['Year']:
                book.publish_date = datetime.date(year=int(isbn_meta['Year']), month=1, day=1)
            r_book = Book.objects.filter(isbn_nb=book.isbn_nb).first()
            if r_book:
                # The book already exists in the database
                book.id = r_book.id
        return book

    def get_nb_copy(self):
        return self.bookcopy_set.count()
    get_nb_copy.short_description = _("Number of samples")

    def has_copies(self):
        return self.get_nb_copy() > 0

    def get_absolute_url(self):
        return reverse('alessandria:book_update', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_on']
        verbose_name = _("Book")
        verbose_name_plural = _("Books")


class BookCopy(ModelEntity):
    number = models.PositiveIntegerField(_("Number"))
    registered_on = models.DateField(_("Registration date"))
    book = models.ForeignKey(Book, verbose_name=_("Book"))
    condition = models.ForeignKey(BookCondition, verbose_name=_("Condition"))
    origin = models.ForeignKey(BookCopyOrigin, verbose_name=_("Origin"))
    price = models.FloatField(_("Price"), blank=True, null=True)
    price_date = models.DateField(_("Date (price)"), blank=True, null=True)
    disabled_on = models.DateField(_("Took out on"), blank=True, null=True)
    notes = models.TextField(_("Notes"), null=True, blank=True)

    # Overriding
    def save(self, *args, **kwargs):
        if not self.pk:
            # Create mode => automatically generate a book copy number
            self.number = BookCopy.objects.filter(book__id=self.book.id).count() + 1
        super(BookCopy, self).save(*args, **kwargs)

    def was_borrowed(self):
        return self.readerborrow_set.count() > 0

    def is_disabled(self):
        return self.disabled_on is not None

    def disabled_on_label(self):  # Convenient function to be accessed from the template
        return self._meta.get_field('disabled_on').verbose_name

    def __str__(self):
        return "%s (%s)" % (str(self.book), self.number)

    class Meta:
        ordering = ['number']
        verbose_name = _("Book sample")
        verbose_name_plural = _("Book samples")


class ReaderBorrowManager(models.Manager):
    def list_all_by_book(self, book_id):
        return self.filter(bookcopy__book__id=book_id)

    def list_current(self):
        return self.filter(returned_on=None)

    def list_late(self):
        return self.filter(returned_on=None, borrow_due_date__lt=datetime.datetime.now())


class ReaderBorrow(ModelEntity):
    reader = models.ForeignKey(Reader, verbose_name=_("Reader"))
    bookcopy = models.ForeignKey(BookCopy, verbose_name=_("Sample"))
    borrowed_date = models.DateField(_("Borrowed on"))
    borrow_due_date = models.DateField(_("Due date"))
    returned_on = models.DateField(_("Returned on"), blank=True, null=True)
    notes = models.TextField(_("Notes"), null=True, blank=True)

    objects = ReaderBorrowManager()

    def clean(self):
        already_borrowed = ReaderBorrow.objects.filter(
            bookcopy__id=self.bookcopy.id
        ).filter(
            returned_on=None
        ).first()
        error = False
        if already_borrowed is not None:
            if self.id:  # Update mode
                if already_borrowed.id != self.id:  # Not updating the current record
                    error = True
            else:  # Create mode
                error = True
            if error:
                raise ValidationError(
                    {'bookcopy': u"Cet exemplaire a été déjà emprunté par %s %s"
                                 % (already_borrowed.reader.first_name, already_borrowed.reader.last_name)}
                )

    def is_returned(self):
        return self.returned_on is not None

    def is_late(self):
        return self.borrow_due_date < datetime.date.today() and not self.is_returned()

    def get_full_name(self):
        if self.borrowed_date:
            return _("Borrowed on %s" % self.borrowed_date)
        return None

    def get_absolute_url(self):
        return reverse('alessandria:reader_borrow_update', kwargs={'pk': self.pk})

    def __str__(self):
        return "%s : %s" % (str(self.reader), str(self.bookcopy.book))

    class Meta:
        ordering = ['borrow_due_date']
        verbose_name = _("Reader borrowing")
        verbose_name_plural = _("Reader borrowings")
