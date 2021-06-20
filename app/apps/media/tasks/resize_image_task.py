import os
import logging
from PIL import Image
from celery.decorators import task
from tempfile import TemporaryFile

from django.core.files.storage import default_storage
from django.conf import settings

from apps.common.utils.file_processor import preserve_original_file, get_base_size, get_watermark_size, \
    get_watermark_top_left


@task(name='resize_image')
def resize_image(filename, watermark, logo_max_width_height_ratio, logo_top_left_ratio, width):
    try:
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

            f = TemporaryFile()
            transparent.save(f, 'PNG')
            f.seek(0)
            length = len(f.read())
            f.seek(0)

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



