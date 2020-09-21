import os
from PIL import Image
from celery import task

from django.core.files.storage import default_storage
from django.conf import settings
from tempfile import TemporaryFile


@task(name='resize_image')
def resize_image(filename, resize_shape):
    # try:
    print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
    print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
    print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
    client = default_storage.client
    img_file = client.get_object(settings.MINIO_STORAGE_MEDIA_BUCKET_NAME,
                                 filename)
    img = Image.open(img_file)
    print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
    print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
    print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
    print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')

    img = img.resize(get_size(img, resize_shape))
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    # image_file = BytesIO()
    img_extension = os.path.splitext(filename)[-1]

    img_name = os.path.splitext(filename)[0]
    resize_img_name = "{}_{}_{}{}".format(img_name, resize_shape[0],
                                          resize_shape[1], img_extension)
    f = TemporaryFile()
    img.save(f, 'JPEG')
    f.seek(0)
    length = len(f.read())
    f.seek(0)
    client.put_object(settings.MINIO_STORAGE_MEDIA_BUCKET_NAME,
                      resize_img_name, f, length, content_type='image/jpeg')
    # except:
    #     print("Unable to resize image: {}".format(filename))


def get_size(img, resize_shape):
    actual_img_width, actual_img_height = img.width, img.height
    ratio = min(resize_shape[0] / actual_img_width,
                resize_shape[1] / actual_img_height)
    return int(actual_img_width * ratio), int(actual_img_height * ratio)
