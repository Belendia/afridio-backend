# Generated by Django 2.2.15 on 2020-09-04 12:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20200903_1744'),
    ]

    operations = [
        migrations.CreateModel(
            name='AudioBook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('word_count', models.PositiveIntegerField()),
                ('estimated_length_in_seconds', models.PositiveIntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=5)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('genres', models.ManyToManyField(to='core.Genre')),
                ('tracks', models.ManyToManyField(to='core.Track')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
