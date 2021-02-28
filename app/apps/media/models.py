import os
from secrets import token_urlsafe
from enum import Enum

from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from django.shortcuts import reverse
from django.dispatch import receiver


def media_image_file_path(instance, filename):
    """Generate file path for new media cover image"""

    ext = filename.split('.')[-1]
    filename = f'cover.{ext}'

    return os.path.join(instance.media_format.lower(),
                        settings.COVER_IMAGE_DIR, instance.slug, filename)


def track_file_path(instance, filename):
    """Generate file path for new track file"""

    ext = filename.split('.')[-1]
    filename = f'track.{ext}'

    folder_name = 'track'
    if instance.medias.all().count() > 0:
        folder_name = instance.medias.all()[0].media_format.lower()

    return os.path.join(folder_name, settings.TRACK_FILE_DIR,
                        instance.slug, filename)


class Genre(models.Model):
    """Genre to be used for a media books and music"""

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
    """Track to be used for a media books and music"""

    name = models.CharField(max_length=255)
    popularity = models.PositiveIntegerField()
    # original_url = models.URLField(max_length=200)
    file_url = models.FileField(null=True, upload_to=track_file_path)
    duration_ms = models.PositiveIntegerField()
    slug = models.SlugField(blank=True, unique=True)
    sample = models.BooleanField(default=False)
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
    authors = models.CharField(max_length=255)
    image = models.ImageField(null=True, upload_to=media_image_file_path)
    slug = models.SlugField(blank=True, unique=True)
    estimated_length_in_seconds = models.PositiveIntegerField(null=True,
                                                              blank=True, )
    rating = models.PositiveIntegerField(null=True, blank=True)
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
        instance.slug = slugify(token_urlsafe(32))


pre_save.connect(pre_save_receiver, sender=Genre)
pre_save.connect(pre_save_receiver, sender=Track)
pre_save.connect(pre_save_receiver, sender=Media)
