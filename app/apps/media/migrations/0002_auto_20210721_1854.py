# Generated by Django 3.2.5 on 2021-07-21 18:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='album_type',
            field=models.CharField(blank=True, choices=[('ALBUM', 'Album'), ('SINGLE', 'Single'), ('COMPILATION', 'Compilation')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='media',
            name='status',
            field=models.CharField(choices=[('UNPUBLISHED', 'Unpublished'), ('PUBLISHED', 'Published'), ('ARCHIVED', 'Archived'), ('TRASHED', 'Trashed')], default='UNPUBLISHED', max_length=15),
        ),
    ]
