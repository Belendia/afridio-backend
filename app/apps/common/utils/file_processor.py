import os
import logging

from django.conf import settings
from django.core.files.storage import default_storage


def preserve_original_file(filename):
    error = True
    try:
        client = default_storage.client
        original_filename = insert_text_in_file_name(filename, '')
        client.copy_object(settings.MINIO_STORAGE_MEDIA_BUCKET_NAME,
                           original_filename,
                           settings.MINIO_STORAGE_MEDIA_BUCKET_NAME + "/" +
                           filename)
        # remove original object
        client.remove_object(settings.MINIO_STORAGE_MEDIA_BUCKET_NAME,
                             filename)
        error = False
    except Exception as ex:
        logging.error("Unable to preserve original file")
        logging.error(ex)

    return original_filename, error


def insert_text_in_file_name(filename, text):
    name = os.path.splitext(filename)[0]
    ext = os.path.splitext(filename)[-1]
    return "{}{}{}".format(name, text, ext)


def replace_ext(filename, ext):
    name = os.path.splitext(filename)[0]
    return "{}.{}".format(name, ext)
