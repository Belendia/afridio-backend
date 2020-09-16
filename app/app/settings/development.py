from .base import * # noqa

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': config('DB_HOST'), # noqa
        'NAME': config('DB_NAME'), # noqa
        'USER': config('DB_USER'), # noqa
        'PASSWORD': config('DB_PASS'), # noqa
    }
}

# Stripe

STRIPE_PUBLIC_KEY = config('STRIPE_TEST_PUBLIC_KEY') # noqa
STRIPE_SECRET_KEY = config('STRIPE_TEST_SECRET_KEY') # noqa

# Send email
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = DEFAULT_FROM_EMAIL = 'pomi144@gmail.com'
EMAIL_HOST_PASSWORD = '#Object123;'
EMAIL_SUBJECT_PREFIX = 'Afridio'
