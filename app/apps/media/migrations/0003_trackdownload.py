# Generated by Django 3.2.5 on 2021-07-30 11:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('media', '0002_auto_20210721_1854'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrackDownload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('DOWNLOADED', 'Downloaded'), ('REMOVED', 'Removed')], max_length=15)),
                ('track', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='media.track')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
