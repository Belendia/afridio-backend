# Generated by Django 2.2.15 on 2021-02-02 13:35

import apps.media.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Track',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('popularity', models.PositiveIntegerField()),
                ('file_url', models.FileField(null=True, upload_to=apps.media.models.track_file_path)),
                ('duration_ms', models.PositiveIntegerField()),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Media',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('price', models.DecimalField(decimal_places=2, max_digits=5)),
                ('discount_price', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('image', models.ImageField(null=True, upload_to=apps.media.models.media_image_file_path)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('estimated_length_in_seconds', models.PositiveIntegerField(blank=True, null=True)),
                ('popularity', models.PositiveIntegerField(blank=True, null=True)),
                ('release_date', models.DateField(null=True)),
                ('description', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('media_format', models.CharField(choices=[('ALBUM', 'ALBUM'), ('AUDIOBOOK', 'AUDIOBOOK'), ('PODCAST', 'PODCAST'), ('NEWSPAPER', 'NEWSPAPER'), ('MAGAZINE', 'MAGAZINE'), ('RADIO', 'RADIO'), ('SPEECH', 'SPEECH'), ('INTERVIEW', 'INTERVIEW'), ('LECTURE', 'LECTURE')], max_length=20)),
                ('word_count', models.PositiveIntegerField(null=True)),
                ('album_type', models.CharField(blank=True, choices=[('ALBUM', 'ALBUM'), ('SINGLE', 'SINGLE'), ('COMPILATION', 'COMPILATION')], max_length=20, null=True)),
                ('genres', models.ManyToManyField(to='media.Genre')),
                ('tracks', models.ManyToManyField(blank=True, related_name='medias', to='media.Track')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
    ]
