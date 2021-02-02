import filetype
import logging
from PIL import Image

from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_image_size(temp_file):
    try:
        img = Image.open(temp_file)
        width, height = img.size
        max_width_height = max(width, height)
    except Exception as ex:
        logging.error(ex)
        raise ValidationError(_('Unable to open file to check size'))

    if max_width_height < 300:
        raise ValidationError(
            _('The minimum width or height of a cover image should be greater '
              'than 300px. [Current width: {}, Current height: {}]'
              .format(width, height)))


def validate_file_type(temp_file):
    kind = filetype.guess(temp_file)
    if kind is None:
        raise ValidationError(
            _("Can't determine file type.")
        )
    file_type = kind.mime
    allowed_types = ['audio/mpeg', 'audio/ogg', 'video/mp4']
    if file_type not in allowed_types:
        raise ValidationError(
          _('File type should be MP3, OGG, WMA or MP4: [Current file type: {}]'
            .format(file_type))
        )
