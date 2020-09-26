import os
import io
import logging
import subprocess

from celery import task
from tempfile import NamedTemporaryFile

from django.core.files.storage import default_storage
from django.conf import settings

from minio.error import ResponseError

from core.models import Media
from common.utils.file_processor import preserve_original_file, \
    insert_text_in_file_name, replace_ext


@task(name='encode_track')
def encode_track(slug, filename):
    original_filename, error = preserve_original_file(filename)
    track_file_name = os.path.basename(filename)
    try:
        client = default_storage.client
        track_file = client.get_object(settings.
                                       MINIO_STORAGE_MEDIA_BUCKET_NAME,
                                       original_filename)
        logging.info('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
        print(track_file_name)
        with open(track_file_name, 'wb') as file_data:
            for d in track_file.stream(32 * 1024):
                file_data.write(d)

        process = subprocess.Popen(['ffmpeg', '-y', '-i', track_file_name,
                                    '-vn', '-c:a', 'aac', '-b:a', '128k',
                                    '-ac', '2', '-r', '48k', '-pass', '2',
                                    replace_ext(insert_text_in_file_name(
                                        track_file_name, '_audio'), "mp4")],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        out, err = process.communicate()

        if process.returncode != 0:
            logging.error(str(err))

        with io.open(track_file_name, 'rb') as f:
            client.put_object(settings.MINIO_STORAGE_MEDIA_BUCKET_NAME,
                              replace_ext(insert_text_in_file_name(
                                  track_file_name, '_audio'), 'mp4'),
                              f, os.path.getsize(track_file_name),
                              content_type='video/mp4')

        os.remove(replace_ext(insert_text_in_file_name(track_file_name,
                                                       '_audio'), "mp4"))
        os.remove(track_file_name)
    except ResponseError as err:
        logging.error(err)

    logging.info('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
