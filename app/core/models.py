import os
import uuid
from enum import Enum
from datetime import date
from secrets import token_urlsafe
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin, Group
from django.conf import settings
from django.db.models.signals import pre_save
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from django.shortcuts import reverse


def media_image_file_path(instance, filename):
    """Generate file path for new media cover image"""

    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('uploads/media/', filename)


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **kwargs):
        """Creates and saves a new user"""

        if not email:
            raise ValueError('Users must have email address')

        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Creates and saves a new superuser"""

        user = self.create_user(email, password,
                                name='admin',
                                sex=User.Sex.UNSURE,
                                date_of_birth=date.today(),
                                phone='+251911000000'
                                )

        user.is_staff = True
        user.is_superuser = True

        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""

    class Sex(Enum):
        MALE = "MALE"
        FEMALE = "FEMALE"
        UNSURE = "UNSURE"

        @classmethod
        def choices(cls):
            return [(key.value, key.name) for key in cls]

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    sex = models.CharField(max_length=20, choices=Sex.choices())
    picture = models.ImageField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True)
    groups = models.ManyToManyField(
        Group,
        blank=True,
        verbose_name=_('groups'),
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        )
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Genre(models.Model):
    """Genre to be used for a audio books and music"""

    name = models.CharField(max_length=255)
    slug = models.SlugField(blank=True, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name


class Track(models.Model):
    """Track to be used for a audio books and music"""

    name = models.CharField(max_length=255)
    popularity = models.PositiveIntegerField()
    original_url = models.URLField(max_length=200)
    duration_ms = models.PositiveIntegerField()
    slug = models.SlugField(blank=True, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name


class Media(models.Model):
    """Common model for Album and Audiobook"""

    # Common fields
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    discount_price = models.DecimalField(null=True, blank=True, max_digits=5,
                                         decimal_places=2)
    image = models.ImageField(null=True, upload_to=media_image_file_path)
    slug = models.SlugField(blank=True, unique=True)
    estimated_length_in_seconds = models.PositiveIntegerField(null=True,
                                                              blank=True,)
    popularity = models.PositiveIntegerField(null=True, blank=True)
    release_date = models.DateField(null=True)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class MediaFormat(Enum):
        ALBUM = "ALBUM"
        AUDIOBOOK = "AUDIOBOOK"
        PODCAST = "PODCAST"
        NEWSPAPER = "NEWSPAPER"
        MAGAZINE = "MAGAZINE"
        RADIO = "RADIO"
        SPEECH = "SPEECH"
        INTERVIEW = "INTERVIEW"
        LECTURE = "LECTURE"

        @classmethod
        def choices(cls):
            return [(key.value, key.name) for key in cls]

    media_format = models.CharField(
        max_length=20,
        choices=MediaFormat.choices()
    )

    # Audiobook
    word_count = models.PositiveIntegerField(null=True)

    # Album
    class AlbumType(Enum):
        ALBUM = "ALBUM"
        SINGLE = "SINGLE"
        COMPILATION = "COMPILATION"

        @classmethod
        def choices(cls):
            return [(key.value, key.name) for key in cls]

    album_type = models.CharField(
        max_length=20,
        choices=AlbumType.choices(),
        null=True,
        blank=True
    )

    # Relationships
    genres = models.ManyToManyField('Genre')
    tracks = models.ManyToManyField('Track')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('ecommerce:media', kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse('ecommerce:add-to-cart', kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse('ecommerce:remove-from-cart', kwargs={
            'slug': self.slug
        })


def pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(token_urlsafe(32))


pre_save.connect(pre_save_receiver, sender=Genre)
pre_save.connect(pre_save_receiver, sender=Track)
pre_save.connect(pre_save_receiver, sender=Media)
