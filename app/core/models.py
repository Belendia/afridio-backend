import os
from enum import Enum
from secrets import token_urlsafe
from allauth.account.signals import user_signed_up

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin, Group
from django.conf import settings
from django.db.models.signals import pre_save
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from django.shortcuts import reverse
from django.dispatch import receiver
from django.core.validators import RegexValidator


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


class UserManager(BaseUserManager):

    def create_user(self, phone, password=None, **kwargs):
        """Creates and saves a new user"""

        if not phone:
            raise ValueError('Users must have phone number')

        if not password:
            raise ValueError('Users must have a password')

        user = self.model(phone=phone, **kwargs)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, phone, password, **extra_fields):
        """Creates and saves a new superuser"""

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""

    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,14}$',
                                 message="Phone number must be entered in the "
                                         "format: '+251911999999'. Up to 14 "
                                         "digits allowed.")

    class Sex(Enum):
        MALE = "MALE"
        FEMALE = "FEMALE"
        UNSURE = "UNSURE"

        @classmethod
        def choices(cls):
            return [(key.value, key.name) for key in cls]

    email = models.EmailField(max_length=255, unique=True, blank=True,
                              null=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, validators=[phone_regex],
                             unique=True)
    date_of_birth = models.DateField(blank=True, null=True)
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

    USERNAME_FIELD = 'phone'

    def __str__(self):
        if self.name:
            return self.name
        return self.phone

    def get_full_name(self):
        if self.name:
            return self.name
        return self.phone

    def get_short_name(self):
        return self.phone


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
                                                              blank=True, )
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


@receiver(user_signed_up)
def user_signed_up(request, user, sociallogin=None, **kwargs):
    """
    When a social account is created successfully and this signal is received,
    django-allauth passes in the sociallogin param, giving access to metadata
    on the remote account, e.g.:

    sociallogin.account.provider  # e.g. 'twitter'
    sociallogin.account.get_avatar_url()
    sociallogin.account.get_profile_url()
    sociallogin.account.extra_data['screen_name']

    See the socialaccount_socialaccount table for more in the 'extra_data'
    field.
    """

    if sociallogin:
        # Extract first / last names from social nets and store on User record
        # if sociallogin.account.provider == 'twitter':
        #     name = sociallogin.account.extra_data['name']
        #     user.first_name = name.split()[0]
        #     user.last_name = name.split()[1]

        if sociallogin.account.provider == 'facebook':
            user.name = sociallogin.account.extra_data['name']
            user.email = sociallogin.account.extra_data['email']

        # if sociallogin.account.provider == 'google':
        #     user.first_name = sociallogin.account.extra_data['given_name']
        #     user.last_name = sociallogin.account.extra_data['family_name']

        user.save()

        try:
            group = Group.objects.get(name='User')
            user.groups.add(group)
            user.save()
        except Group.DoesNotExist:
            pass


def pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(token_urlsafe(32))


pre_save.connect(pre_save_receiver, sender=Genre)
pre_save.connect(pre_save_receiver, sender=Track)
pre_save.connect(pre_save_receiver, sender=Media)
