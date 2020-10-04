from django.contrib import admin
from . import models


class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ['number', 'verified']


admin.site.register(models.PhoneNumber, PhoneNumberAdmin)
