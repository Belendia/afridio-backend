# Generated by Django 2.2.24 on 2021-06-21 11:07

import apps.common.utils.validators
import apps.media.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0004_auto_20210620_1612'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='featured',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='image',
            name='file',
            field=models.ImageField(null=True, upload_to=apps.media.models.image_file_path, validators=[apps.common.utils.validators.validate_image_size]),
        ),
        migrations.AlterField(
            model_name='track',
            name='file_url',
            field=models.FileField(null=True, upload_to=apps.media.models.track_file_path, validators=[apps.common.utils.validators.validate_file_type]),
        ),
    ]