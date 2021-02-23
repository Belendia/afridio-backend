# Generated by Django 2.2.18 on 2021-02-04 19:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('phone', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PhoneVerification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('phone_number', models.CharField(blank=True, max_length=17, verbose_name='Phone Number')),
                ('security_code', models.CharField(max_length=120, verbose_name='Security Code')),
                ('session_token', models.CharField(max_length=500, verbose_name='Device Session Token')),
                ('is_verified', models.BooleanField(default=False, verbose_name='Security Code Verified')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='phonenumber', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Phone Number Verification',
                'verbose_name_plural': 'Phone Number Verifications',
                'ordering': ['-created_at', '-updated_at'],
                'unique_together': {('security_code', 'phone_number', 'session_token')},
            },
        ),
        migrations.DeleteModel(
            name='PhoneNumber',
        ),
    ]