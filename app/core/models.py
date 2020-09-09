import os
import uuid
from enum import Enum
from secrets import token_urlsafe
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin, Group
from django.conf import settings
from django.db.models.signals import pre_save
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify


def audiobook_image_file_path(instance, filename):
    """Generate file path for new audiobook cover image"""

    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('uploads/audiobook/', filename)


def album_image_file_path(instance, filename):
    """Generate file path for new album cover image"""

    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('uploads/album/', filename)


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

        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True

        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    groups = models.ManyToManyField(
        Group,
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


class AudioBook(models.Model):
    """AudioBook object"""

    title = models.CharField(max_length=255)
    word_count = models.PositiveIntegerField()
    estimated_length_in_seconds = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    image = models.ImageField(null=True, upload_to=audiobook_image_file_path)
    slug = models.SlugField(blank=True, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

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


class Album(models.Model):
    """Album object"""

    class AlbumType(Enum):
        ALBUM = "ALBUM"
        SINGLE = "SINGLE"
        COMPILATION = "COMPILATION"

        @classmethod
        def choices(cls):
            return [(key.value, key.name) for key in cls]

    name = models.CharField(max_length=255)
    album_type = models.CharField(
        max_length=20,
        choices=AlbumType.choices()
    )
    estimated_length_in_seconds = models.PositiveIntegerField()
    popularity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    release_date = models.DateField()
    image = models.ImageField(null=True, upload_to=album_image_file_path)
    slug = models.SlugField(blank=True, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    genres = models.ManyToManyField('Genre')
    tracks = models.ManyToManyField('Track')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name


def pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(token_urlsafe(16))


pre_save.connect(pre_save_receiver, sender=Genre)
pre_save.connect(pre_save_receiver, sender=Track)
pre_save.connect(pre_save_receiver, sender=AudioBook)
pre_save.connect(pre_save_receiver, sender=Album)
