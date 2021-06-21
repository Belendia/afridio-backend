from django.contrib import admin
from . import models


class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'security_code', 'is_verified')
    search_fields = ("phone_number",)
    list_filter = ("is_verified",)


admin.site.register(models.PhoneVerification, PhoneNumberAdmin)
