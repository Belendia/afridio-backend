from .base import * # noqa

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS += [
    'minio_storage'
]

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

# Minio
DEFAULT_FILE_STORAGE = "minio_storage.storage.MinioMediaStorage"
STATICFILES_STORAGE = "minio_storage.storage.MinioStaticStorage"
MINIO_STORAGE_ENDPOINT = config('MINIO_STORAGE_ENDPOINT') # noqa
MINIO_STORAGE_ACCESS_KEY = config('MINIO_STORAGE_ACCESS_KEY') # noqa
MINIO_STORAGE_SECRET_KEY = config('MINIO_STORAGE_SECRET_KEY') # noqa
MINIO_STORAGE_USE_HTTPS = False
MINIO_STORAGE_MEDIA_BUCKET_NAME = 'media'
MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = True
MINIO_STORAGE_STATIC_BUCKET_NAME = 'static'
MINIO_STORAGE_AUTO_CREATE_STATIC_BUCKET = True

# Celery
BROKER_URL = config('DEV_CELERY_BROKER') # noqa
CELERY_RESULT_BACKEND = config('DEV_CELERY_RESULT_BACKEND') # noqa
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Africa/Addis_Ababa'