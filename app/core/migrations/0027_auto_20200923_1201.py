# Generated by Django 2.2.15 on 2020-09-23 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_auto_20200923_1053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='tracks',
            field=models.ManyToManyField(blank=True, related_name='medias', to='core.Track'),
        ),
    ]