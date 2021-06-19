from django.contrib import admin

from apps.media import models

admin.site.register(models.Genre)
admin.site.register(models.Track)
admin.site.register(models.Media)
admin.site.register(models.Language)
admin.site.register(models.Format)
admin.site.register(models.Author)
admin.site.register(models.Image)
admin.site.register(models.ImageSize)
