from django.contrib import admin

from apps.media import models

admin.site.register(models.Genre)
admin.site.register(models.Language)
admin.site.register(models.Format)
admin.site.register(models.ImageSize)


class ImageAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


admin.site.register(models.Image, ImageAdmin)


class TrackAdmin(admin.ModelAdmin):
    list_display = ("name", "sample", "created_at")
    search_fields = ("name",)
    list_filter = ("duration", "popularity", "sample")
    filter_horizontal = ('medias', )


admin.site.register(models.Track, TrackAdmin)


class MediaAdmin(admin.ModelAdmin):
    list_display = ("title", "language", "featured", "release_date", "created_at")
    list_filter = ("featured", "language", "release_date")
    search_fields = ("title",)
    filter_horizontal = ('authors', 'genres', 'images', 'tracks')


admin.site.register(models.Media, MediaAdmin)


class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "sex", "created_at")
    list_filter = ("sex",)
    search_fields = ("name",)


admin.site.register(models.Author, AuthorAdmin)
