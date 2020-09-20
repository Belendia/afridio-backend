from app.settings.base import * # noqa


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["afridio.com"]

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

STRIPE_PUBLIC_KEY = config('STRIPE_LIVE_PUBLIC_KEY') # noqa
STRIPE_SECRET_KEY = config('STRIPE_LIVE_SECRET_KEY') # noqa

# Send email
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = DEFAULT_FROM_EMAIL = 'pomi144@gmail.com'
EMAIL_HOST_PASSWORD = '#Object123;'
EMAIL_SUBJECT_PREFIX = 'Afridio'

# s3 setting
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_STORAGE_BUCKET_NAME = 'media'
AWS_S3_REGION_NAME = 'eu-west-2'
