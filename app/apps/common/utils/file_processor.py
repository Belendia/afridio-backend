import os
import logging

from django.conf import settings
from django.core.files.storage import default_storage


def preserve_original_file(filename):
    error = True
    original_filename = None
    try:
        client = default_storage.client
        original_filename = insert_text_in_file_name(filename, '-original')
        client.copy_object(settings.MINIO_STORAGE_MEDIA_BUCKET_NAME,
                           original_filename,
                           settings.MINIO_STORAGE_MEDIA_BUCKET_NAME + "/" +
                           filename)

        # remove original object
        # client.remove_object(settings.MINIO_STORAGE_MEDIA_BUCKET_NAME,
        #                      filename)
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


def get_base_size(uploaded_image, width):
    actual_img_width, actual_img_height = uploaded_image.width, uploaded_image.height
    ratio = width / actual_img_width
    return int(actual_img_width * ratio), int(actual_img_height * ratio)


def get_watermark_size(uploaded_image, logo_max_width_height_ratio):
    max_width_height = max(uploaded_image.width, uploaded_image.height)
    return (int(max_width_height * logo_max_width_height_ratio),
            int(max_width_height * logo_max_width_height_ratio))


def get_watermark_top_left(water_mark_image, logo_top_left_ratio):
    actual_img_width, actual_img_height = water_mark_image.width, water_mark_image.height
    return (int(actual_img_width * logo_top_left_ratio),
            int(actual_img_height * logo_top_left_ratio))