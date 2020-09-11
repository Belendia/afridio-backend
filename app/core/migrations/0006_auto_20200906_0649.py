# Generated by Django 2.2.15 on 2020-09-06 06:49

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_album'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='image',
            field=models.ImageField(null=True, upload_to=core.models.media_image_file_path),
        ),
        migrations.AddField(
            model_name='audiobook',
            name='image',
            field=models.ImageField(null=True, upload_to=core.models.media_image_file_path),
        ),
    ]
