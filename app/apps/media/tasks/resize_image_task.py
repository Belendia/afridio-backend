import os
import logging
from PIL import Image
from celery.decorators import task
from tempfile import TemporaryFile

from django.core.files.storage import default_storage
from django.conf import settings

from apps.media.models import Media
from apps.common.utils.file_processor import preserve_original_file


@task(name='resize_image')
def resize_image(slug, filename):

    if settings.COVER_IMAGE_CROP_SIZES.__len__() > 0:
        original_filename, error = preserve_original_file(filename)

        if error:
            return

    try:
        for i, resize_shape in enumerate(settings.COVER_IMAGE_CROP_SIZES):
            client = default_storage.client
            img_file = client.get_object(settings.
                                         MINIO_STORAGE_MEDIA_BUCKET_NAME,
                                         filename)

            base_img = Image.open(img_file).convert("RGBA")

            transparent = Image.new('RGBA', base_img.size, (0, 0, 0, 0))
            transparent.paste(base_img, (0, 0))

            if settings.WATERMARK_COVER_IMAGE:
                logo_file = client.get_object(settings.
                                              MINIO_STORAGE_STATIC_BUCKET_NAME,
                                              'img/logo.png')
                watermark_img = Image.open(logo_file).convert("RGBA")
                # resize watermark
                watermark_img = watermark_img.resize(
                    get_watermark_size(base_img))
                transparent.paste(watermark_img,
                                  get_watermark_top_left(base_img),
                                  mask=watermark_img)

            transparent = transparent.resize(get_base_size(base_img,
                                                           resize_shape))

            img_name = os.path.splitext(filename)[0]
            resize_img_name = "{}-{}.{}".format(img_name, resize_shape[0],
                                                'png')

            f = TemporaryFile()
            transparent.save(f, 'PNG')
            f.seek(0)
            length = len(f.read())
            f.seek(0)

            if i == 0:
                resize_img_name = "{}.{}".format(img_name, 'png')
                try:
                    media = Media.objects.get(slug=slug)
                    media.image.name = resize_img_name
                    media.save()
                except Media.DoesNotExist:
                    logging.error("Media with slug: {} Not found. Unable to "
                                  "update file in media".format(slug))

            # save the modified object
            client.put_object(settings.MINIO_STORAGE_MEDIA_BUCKET_NAME,
                              resize_img_name, f, length,
                              content_type='image/png')
            logging.info("saved")
    except Exception as ex:
        logging.error("Unable to resize image: {}".format(filename))
        logging.error(ex)


def get_base_size(img, resize_shape):
    actual_img_width, actual_img_height = img.width, img.height
    ratio = min(resize_shape[0] / actual_img_width,
                resize_shape[1] / actual_img_height)
    return int(actual_img_width * ratio), int(actual_img_height * ratio)


def get_watermark_size(img):
    max_width_height = max(img.width, img.height)
    return (int(max_width_height * settings.LOGO_MAX_WIDTH_HEIGHT_RATIO),
            int(max_width_height * settings.LOGO_MAX_WIDTH_HEIGHT_RATIO))


def get_watermark_top_left(img):
    actual_img_width, actual_img_height = img.width, img.height
    return (int(actual_img_width * settings.LOGO_TOP_LEFT_RATIO),
            int(actual_img_height * settings.LOGO_TOP_LEFT_RATIO))
