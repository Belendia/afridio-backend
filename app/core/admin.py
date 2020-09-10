from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _

from core import models


class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {
            'fields': ('name', 'sex', 'date_of_birth', 'phone', 'picture')
        }),
        (
            _('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser')}
        ),
        ('Groups', {'fields': ('groups',)}),
        ('Permissions', {'fields': ('user_permissions',)}),
        (_('Important dates'), {'fields': ('last_login', )}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide', ),
            'fields': ('email', 'password1', 'password2'),
        }),
        (_('Personal Info'), {
            'fields': ('name', 'sex', 'date_of_birth', 'phone', 'picture')
        }),
        (
            _('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser')}
        ),
        ('Groups', {'fields': ('groups',)}),
        ('Permissions', {'fields': ('user_permissions',)}),
    )
    filter_horizontal = ('groups', 'user_permissions',)


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Genre)
admin.site.register(models.Track)
admin.site.register(models.AudioBook)
admin.site.register(models.Album)
