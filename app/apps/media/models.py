import os
from secrets import token_urlsafe
from enum import Enum
import random

from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save, post_save
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from django.shortcuts import reverse
from django.dispatch import receiver

from ..common.models import TimeStampedModel
from apps.media.tasks.resize_image_task import resize_image
from apps.common.utils.validators import validate_image_size, validate_file_type


def image_file_path(instance, filename):
    """Generate file path for new media cover image"""

    filename = "{}.{}".format(instance.slug, 'png')

    return os.path.join(settings.IMAGE_DIR, "w{}".format(instance.size.width), filename)


def track_file_path(instance, filename):
    """Generate file path for new track file"""

    ext = filename.split('.')[-1]
    filename = "{}.{}".format(instance.slug, ext)

    return os.path.join(settings.TRACK_FILE_DIR, filename)


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


class Format(TimeStampedModel):
    name = models.CharField(max_length=50)
    slug = models.SlugField(blank=True, unique=True)
    sequence = models.PositiveIntegerField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    class Meta:
        ordering = ['-sequence']

    def __str__(self):
        return self.name


class ImageSize(TimeStampedModel):
    name = models.CharField(max_length=50)
    slug = models.SlugField(blank=True, unique=True)
    width = models.PositiveIntegerField()
    watermark = models.BooleanField()
    logo_max_width_height_ratio = models.FloatField(default=0.06)
    logo_top_left_ratio = models.FloatField(default=0.02)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    class Meta:
        ordering = ['-width']

    def __str__(self):
        return str(self.name)


class Image(TimeStampedModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(blank=True, unique=True)
    file = models.ImageField(null=True, upload_to=image_file_path, validators=[validate_image_size])
    size = models.ForeignKey(
        ImageSize,
        on_delete=models.PROTECT
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    def __str__(self):
        return "{} - ({})".format(self.name, self.size)


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

    images = models.ManyToManyField('Image')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    class Meta:
        ordering = ['-name']

    def __str__(self):
        return self.name


class Narrator(TimeStampedModel):
    name = models.CharField(max_length=50)
    slug = models.SlugField(blank=True, unique=True)

    class Sex(Enum):
        MALE = "MALE"
        FEMALE = "FEMALE"
        UNSURE = "UNSURE"

        @classmethod
        def choices(cls):
            return [(key.value, key.name) for key in cls]

    sex = models.CharField(max_length=20, choices=Sex.choices())

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

    slug = models.SlugField(blank=True, unique=True)
    estimated_length_in_seconds = models.PositiveIntegerField(null=True,
                                                              blank=True)
    release_date = models.DateField(null=True)
    description = models.TextField()
    featured = models.BooleanField(default=False)

    # Audiobook
    word_count = models.PositiveIntegerField(null=True)

    # Album
    class AlbumType(models.TextChoices):
        ALBUM = "ALBUM"
        SINGLE = "SINGLE"
        COMPILATION = "COMPILATION"

    album_type = models.CharField(
        max_length=20,
        choices=AlbumType.choices,
        null=True,
        blank=True
    )

    # Status
    class StatusType(models.TextChoices):
        UNPUBLISHED = "UNPUBLISHED"
        PUBLISHED = "PUBLISHED"
        ARCHIVED = "ARCHIVED"
        TRASHED = "TRASHED"

    status = models.CharField(
        max_length=15,
        choices=StatusType.choices,
        default=StatusType.UNPUBLISHED
    )

    # Relationships
    media_format = models.ForeignKey(Format, on_delete=models.PROTECT)
    language = models.ForeignKey(Language, on_delete=models.PROTECT)
    genres = models.ManyToManyField('Genre')
    tracks = models.ManyToManyField('Track', blank=True)
    images = models.ManyToManyField('Image')
    authors = models.ManyToManyField('Author')
    narrators = models.ManyToManyField('Narrator')
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

    def get_status_type(self):
        return StatusType(self.status).name.title()

    def is_liked(self, user):
        ml = self.medialike_set.filter(user=user)
        if ml.exists() and ml.count() > 0:
            return ml[0].liked
        return False

    def get_rating(self):
        rating = self.medialike_set.filter(liked=True).count()
        if rating >= 1000000000:
            rating = "%.0f%s" % (rating / 1000000000.00, 'B')
        elif rating >= 1000000:
            rating = "%.0f%s" % (rating / 1000000.00, 'M')
        elif rating >= 1000:
            rating = "%.0f%s" % (rating / 1000.0, 'K')
        return str(rating)


class Track(TimeStampedModel):
    """Track to be used for a media books and music"""

    name = models.CharField(max_length=255)
    popularity = models.PositiveIntegerField()
    # original_url = models.URLField(max_length=200)
    file_url = models.FileField(null=True, upload_to=track_file_path, validators=[validate_file_type])
    duration = models.PositiveIntegerField()
    slug = models.SlugField(blank=True, unique=True)
    sample = models.BooleanField(default=False)
    sequence = models.PositiveIntegerField()

    medias = models.ManyToManyField(Media, through=Media.tracks.through, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    class Meta:
        ordering = ['-sequence', '-id']

    def __str__(self):
        return self.name

    def is_downloaded(self, user):
        td = self.trackdownload_set.filter(user=user).order_by('-created_at')
        if td.exists() and td.count() > 0:
            return td[0].status == 'DOWNLOADED'
        return False


class TrackDownload(TimeStampedModel):
    """Logs the download and removal of a track"""
    track = models.ForeignKey(
        'track',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    # Status
    class StatusType(models.TextChoices):
        DOWNLOADED = "DOWNLOADED"
        REMOVED = "REMOVED"

    status = models.CharField(
        max_length=15,
        choices=StatusType.choices
    )

    def __str__(self):
        return "{} - {} - {}".format(self.user.name, self.track.name, self.status)


class MediaLike(TimeStampedModel):
    """Logs the likes of a media"""
    media = models.ForeignKey(
        'media',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )
    liked = models.BooleanField(default=True)

    def __str__(self):
        return "{} - {} - {}".format(self.user.name, self.media.title, self.liked)


def pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(token_urlsafe(16))


# resize image when user uploads it using admin interface
def post_save_receiver(sender, instance, *args, **kwargs):
    if instance.file:
        resize_image.delay(instance.file.name, instance.size.watermark, instance.size.logo_max_width_height_ratio,
                           instance.size.logo_top_left_ratio, instance.size.width)


pre_save.connect(pre_save_receiver, sender=Genre)
pre_save.connect(pre_save_receiver, sender=Track)
pre_save.connect(pre_save_receiver, sender=Media)
pre_save.connect(pre_save_receiver, sender=Author)
pre_save.connect(pre_save_receiver, sender=Format)
pre_save.connect(pre_save_receiver, sender=Language)
pre_save.connect(pre_save_receiver, sender=ImageSize)
pre_save.connect(pre_save_receiver, sender=Image)
pre_save.connect(pre_save_receiver, sender=Narrator)

post_save.connect(post_save_receiver, sender=Image)
