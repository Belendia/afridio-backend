# Generated by Django 2.2.24 on 2021-06-21 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0006_auto_20210621_1325'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='format',
            options={'ordering': ['-sequence']},
        ),
        migrations.AddField(
            model_name='format',
            name='sequence',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
    ]