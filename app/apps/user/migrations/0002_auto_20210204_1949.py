# Generated by Django 2.2.18 on 2021-02-04 19:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='phone',
            new_name='phone_number',
        ),
    ]
