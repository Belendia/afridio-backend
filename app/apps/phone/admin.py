from django.contrib import admin
from . import models


class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'is_verified']


admin.site.register(models.PhoneVerification, PhoneNumberAdmin)
