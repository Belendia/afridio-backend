import os
import io
import logging
import subprocess

from celery import task

from django.core.files.storage import default_storage
from django.conf import settings

from minio.error import ResponseError

from core.models import Media
from common.utils.file_processor import preserve_original_file, \
    insert_text_in_file_name, replace_ext


@task(name='encode_track')
def encode_track(slug, filename):
    cloud_filename, error = preserve_original_file(filename)
    offline_filename = os.path.basename(filename)

    try:
        client = default_storage.client
        if download_file(cloud_filename, offline_filename):
            # file is download form s3, continue processing the file

            # encode with 96k and 128k bit-rate for mobile and desktop
            for rate in ['96k', '128k']:
                mp4_offline_filename = replace_ext(insert_text_in_file_name(
                    offline_filename, '-{}'.format(rate)), "mp4")
                mp4_cloud_filename_with_path = replace_ext(
                    insert_text_in_file_name(filename, '-{}'.format(rate)),
                    "mp4")
                if encode_audio(offline_filename, mp4_offline_filename, rate):
                    upload_audio(mp4_offline_filename,
                                 mp4_cloud_filename_with_path)

                os.remove(mp4_offline_filename)

            os.remove(offline_filename)
    except ResponseError as err:
        logging.error(err)


def download_file(cloud_filename, offline_filename):
    try:
        client = default_storage.client
        track_file = client.get_object(settings.
                                       MINIO_STORAGE_MEDIA_BUCKET_NAME,
                                       cloud_filename)

        with open(offline_filename, 'wb') as file_data:
            for d in track_file.stream(32 * 1024):
                file_data.write(d)
    except ResponseError as err:
        logging.error(err)
        return False

    return True


def encode_audio(offline_filename, mp4_offline_filename, bitrate):
    process = subprocess.Popen(['ffmpeg', '-y', '-i', offline_filename,
                                '-vn', '-c:a', 'aac', '-b:a', bitrate,
                                '-ac', '2', '-r', '48k', '-pass', '2',
                                mp4_offline_filename],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    out, err = process.communicate()

    if process.returncode != 0:
        logging.error(str(err))
        return False

    return True


def upload_audio(mp4_offline_filename, mp4_cloud_filename_with_path):
    client = default_storage.client
    with open(mp4_offline_filename, 'rb') as f:
        buffer = io.BytesIO(f.read())
        client.put_object(settings.MINIO_STORAGE_MEDIA_BUCKET_NAME,
                          mp4_cloud_filename_with_path, buffer,
                          os.path.getsize(mp4_offline_filename),
                          content_type='video/mp4')

