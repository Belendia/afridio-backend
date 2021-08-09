from enum import Enum

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin, Group
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):

    def create_user(self, phone_number, password=None, **kwargs):
        """Creates and saves a new account"""

        if not phone_number:
            raise ValueError('Users must have phone number')

        if not password:
            raise ValueError('Users must have a password')

        user = self.model(phone_number=phone_number, **kwargs)
        user.set_password(password)
        if kwargs.get('email'):
            user.email = self.normalize_email(kwargs.get('email'))
        user.save(using=self._db)

        return user

    def create_superuser(self, phone_number, password, **extra_fields):
        """Creates and saves a new superuser"""

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom account model that supports using email instead of username"""

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

    phone_number = models.CharField(max_length=15, validators=[phone_regex],
                                    unique=True)
    email = models.EmailField(max_length=255, unique=True, blank=True,
                              null=True)
    name = models.CharField(max_length=255)
    date_of_birth = models.DateField(blank=True, null=True)
    sex = models.CharField(max_length=20, choices=Sex.choices(), blank=True, null=True)
    picture = models.ImageField(blank=True, null=True)
    slug = models.CharField(max_length=100, null=True, blank=True)
    enable_2fa = models.BooleanField(default=False)
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

    USERNAME_FIELD = 'phone_number'

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        if self.name:
            return self.name
        return self.phone_number

    def get_full_name(self):
        if self.name:
            return self.name
        return self.phone_number

    def get_short_name(self):
        return self.phone_number
