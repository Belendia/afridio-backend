import os
from secrets import token_urlsafe
from enum import Enum
import random

from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from django.shortcuts import reverse
from django.dispatch import receiver
from ..common.models import TimeStampedModel


def media_image_file_path(instance, filename):
    """Generate file path for new media cover image"""

    ext = filename.split('.')[-1]
    filename = f'cover.{ext}'

    return os.path.join(instance.media_format.name.lower(),
                        settings.COVER_IMAGE_DIR, instance.slug, filename)


def track_file_path(instance, filename):
    """Generate file path for new track file"""

    ext = filename.split('.')[-1]
    filename = f'track.{ext}'

    folder_name = 'track'
    if instance.medias.all().count() > 0:
        folder_name = instance.medias.all()[0].media_format.name.lower()

    return os.path.join(folder_name, settings.TRACK_FILE_DIR,
                        instance.slug, filename)


class Genre(TimeStampedModel):
    """Genre to be used for a media books and music"""

    name = models.CharField(max_length=255)
    slug = models.SlugField(blank=True, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name


class Track(TimeStampedModel):
    """Track to be used for a media books and music"""

    name = models.CharField(max_length=255)
    popularity = models.PositiveIntegerField()
    # original_url = models.URLField(max_length=200)
    file_url = models.FileField(null=True, upload_to=track_file_path)
    duration = models.PositiveIntegerField()
    slug = models.SlugField(blank=True, unique=True)
    sample = models.BooleanField(default=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name


class Format(TimeStampedModel):
    name = models.CharField(max_length=50)
    slug = models.SlugField(blank=True, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    class Meta:
        ordering = ['-name']

    def __str__(self):
        return self.name


class Language(TimeStampedModel):
    name = models.CharField(max_length=50)
    slug = models.SlugField(blank=True, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    class Meta:
        ordering = ['-name']

    def __str__(self):
        return self.name


class Author(TimeStampedModel):
    name = models.CharField(max_length=50)
    slug = models.SlugField(blank=True, unique=True)
    biography = models.TextField(blank=True, null=True)

    class Sex(Enum):
        MALE = "MALE"
        FEMALE = "FEMALE"
        UNSURE = "UNSURE"

        @classmethod
        def choices(cls):
            return [(key.value, key.name) for key in cls]

    sex = models.CharField(max_length=20, choices=Sex.choices())
    date_of_birth = models.DateField(blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    class Meta:
        ordering = ['-name']

    def __str__(self):
        return self.name


class Media(TimeStampedModel):
    """Common model for Album and Audiobook"""

    # Common fields
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    discount_price = models.DecimalField(null=True, blank=True, max_digits=5,
                                         decimal_places=2)

    authors = models.ManyToManyField('Author')
    image = models.ImageField(null=True, upload_to=media_image_file_path)
    slug = models.SlugField(blank=True, unique=True)
    estimated_length_in_seconds = models.PositiveIntegerField(null=True,
                                                              blank=True, )
    rating = models.PositiveIntegerField(null=True, blank=True)
    release_date = models.DateField(null=True)
    description = models.TextField()

    media_format = models.ForeignKey(Format, on_delete=models.PROTECT)
    language = models.ForeignKey(Language, on_delete=models.PROTECT)

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
    tracks = models.ManyToManyField('Track', related_name='medias',
                                    blank=True)
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
        instance.slug = slugify(token_urlsafe(16))


pre_save.connect(pre_save_receiver, sender=Genre)
pre_save.connect(pre_save_receiver, sender=Track)
pre_save.connect(pre_save_receiver, sender=Media)
pre_save.connect(pre_save_receiver, sender=Author)
pre_save.connect(pre_save_receiver, sender=Format)
pre_save.connect(pre_save_receiver, sender=Language)
