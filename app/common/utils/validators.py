# from mimetypes import MimeTypes
from PIL import Image

from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_image_size(temp_file):
    try:
        img = Image.open(temp_file)
        width, height = img.size
        max_width_height = max(width, height)
    except:
        raise ValidationError(_('Unable to open file to check size'))

    if max_width_height < 300:
        raise ValidationError(
            _('The minimum width or height of a cover image should be greater '
              'than 300px. [Current width: {}, Current height: {}]'
              .format(width, height)))

# def validate_file_type(temp_file):
#     mime = MimeTypes()
#     file_type = mime.guess_type(temp_file)
#     allowed_types = ['image/jpeg', 'image/png']
#     if file_type[0] not in allowed_types:
#         return ValidationError(
#             _('File type should be PNG or JPEG: [Current file type: %(type)]'),
#             params={'type': file_type[0]},
#         )
