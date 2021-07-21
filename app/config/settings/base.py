"""
Django settings for app project.

Generated by 'django-admin startproject' using Django 2.2.15.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from decouple import config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# Application definition

INSTALLED_APPS = [
    # 'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # django rest frameworks
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_nested',

    # for django forms
    'crispy_forms',

    # Local apps
    'apps.account',
    'apps.media',
    'apps.ecommerce',
    'apps.phone',
    'apps.common',

    # Admin template
    'admin_interface',
    'colorfield',
    'django.contrib.admin',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        }
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATIC_ROOT = '/vol/web/static'
MEDIA_ROOT = '/vol/web/media'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

AUTH_USER_MODEL = 'account.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_VERSIONING_CLASS':
        'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_VERSION': 'v1'
}

LOGIN_REDIRECT_URL = '/'

# CRISPY FORMS

CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Image manipulation
IMAGE_DIR = 'images'

# Track File
TRACK_FILE_DIR = 'audio'

# Twilio

PHONE_VERIFICATION = {
    'BACKEND': 'apps.phone.backends.twilio.TwilioBackend',
    'OPTIONS': {
        'SID': config('TWILIO_ACCOUNT_SID'),
        'SECRET': config('TWILIO_AUTH_TOKEN'),
        'FROM': config('TWILIO_PHONE'),
        "SANDBOX_TOKEN": config('TWILIO_AUTH_TOKEN'),
    },
    "TOKEN_LENGTH": 6,
    "MESSAGE": "Welcome to {app}! Please use security code {security_code} to proceed.",
    "APP_NAME": "Afridio",
    "SECURITY_CODE_EXPIRATION_TIME": 3600,  # One hour
    "VERIFY_SECURITY_CODE_ONLY_ONCE": False,
    # If False, then a security code can be used multiple times for verification
    "OTP_RESEND_TIME": 300,  # 5 minutes
}

# django admin interface
X_FRAME_OPTIONS = 'SAMEORIGIN'
