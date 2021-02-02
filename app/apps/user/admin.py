from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _

from apps.user import models


class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['phone', 'name']
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        (_('Personal Info'), {
            'fields': ('name', 'sex', 'date_of_birth', 'email', 'picture')
        }),
        (_('Auth'), {
            'fields': ('enable_2fa', 'slug')
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
            'fields': ('phone', 'password1', 'password2'),
        }),
        (_('Personal Info'), {
            'fields': ('name', 'sex', 'date_of_birth', 'email', 'picture')
        }),
        (_('Auth'), {
            'fields': ('enable_2fa', 'slug')
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
