from django.contrib import admin

from apps.media import models


admin.site.register(models.Genre)
admin.site.register(models.Track)
admin.site.register(models.Media)
