# Generated by Django 2.2.15 on 2020-09-09 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20200909_1553'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(to='auth.Group'),
        ),
    ]
