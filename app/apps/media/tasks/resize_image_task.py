import os
import logging
from PIL import Image
from celery.decorators import task
from tempfile import TemporaryFile

from django.core.files.storage import default_storage
from django.conf import settings

# from apps.media.models import Media
from apps.common.utils.file_processor import preserve_original_file


@task(name='resize_image')
def resize_image(filename, watermark, logo_max_width_height_ratio, logo_top_left_ratio, width):
    # if settings.COVER_IMAGE_CROP_SIZES.__len__() > 0:
    #     original_filename, error = preserve_original_file(instance.filename)
    #
    #     if error:
    #         return

    try:
        # for i, resize_shape in enumerate(settings.COVER_IMAGE_CROP_SIZES):

        if filename:
            client = default_storage.client
            img_file = client.get_object(settings.
                                         MINIO_STORAGE_MEDIA_BUCKET_NAME,
                                         filename)

            base_img = Image.open(img_file).convert("RGBA")

            transparent = Image.new('RGBA', base_img.size, (0, 0, 0, 0))
            transparent.paste(base_img, (0, 0))

            if watermark:
                logo_file = client.get_object(settings.
                                              MINIO_STORAGE_STATIC_BUCKET_NAME,
                                              'img/logo.png')
                watermark_img = Image.open(logo_file).convert("RGBA")
                # resize watermark
                watermark_img = watermark_img.resize(get_watermark_size(base_img, logo_max_width_height_ratio))
                transparent.paste(watermark_img, get_watermark_top_left(base_img, logo_top_left_ratio),
                                  mask=watermark_img)

            transparent = transparent.resize(get_base_size(base_img, width))

            # img_name = os.path.splitext(filename)[0]
            # resize_img_name = "{}{}-w{}.{}".format(slug, id, width, 'png')

            f = TemporaryFile()
            transparent.save(f, 'PNG')
            f.seek(0)
            length = len(f.read())
            f.seek(0)

            # resize_img_name = "{}.{}".format(img_name, 'png')
            # try:
            #     uploaded_image.path.name = resize_img_name
            #     uploaded_image.save()
            # except Media.DoesNotExist:
            #     logging.error("Image with slug: {} Not found. Unable to "
            #                   "update file in image".format(slug))

            # save the modified object
            client.put_object(settings.MINIO_STORAGE_MEDIA_BUCKET_NAME,
                              filename, f, length,
                              content_type='image/png')
            logging.info("Image is resized successfully")
        else:
            logging.info("Unable to find image to resize")
    except Exception as ex:
        logging.error("Unable to resize image: {}".format(filename))
        logging.error(ex)


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
