from django.contrib import admin

from apps.media import models

admin.site.register(models.Genre)
admin.site.register(models.Language)
admin.site.register(models.Format)


class ImageSizeAdmin(admin.ModelAdmin):
    list_display = ("name", "width", "watermark", "created_at")
    list_filter = ("watermark", )
    search_fields = ("name", "width")


admin.site.register(models.ImageSize, ImageSizeAdmin)


class ImageAdmin(admin.ModelAdmin):
    list_display = ("name", "size", "created_at")
    list_filter = ("size",)
    search_fields = ("name",)


admin.site.register(models.Image, ImageAdmin)


class TrackAdmin(admin.ModelAdmin):
    list_display = ("name", "sequence", "sample", "created_at")
    search_fields = ("name",)
    list_filter = ("duration", "medias", "popularity", "sample")
    filter_horizontal = ('medias', )


admin.site.register(models.Track, TrackAdmin)


class MediaAdmin(admin.ModelAdmin):
    list_display = ("title", "language", "status", "featured", "release_date", "created_at")
    list_filter = ("authors", "featured", "genres", "language", "media_format", "narrators", "status", "release_date")
    search_fields = ("title",)
    filter_horizontal = ('authors', 'genres', 'images', 'tracks', 'narrators')


admin.site.register(models.Media, MediaAdmin)


class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "sex", "created_at")
    list_filter = ("sex",)
    search_fields = ("name",)
    filter_horizontal = ('images',)


admin.site.register(models.Author, AuthorAdmin)


class NarratorAdmin(admin.ModelAdmin):
    list_display = ("name", "sex", "created_at")
    list_filter = ("sex",)
    search_fields = ("name",)


admin.site.register(models.Narrator, NarratorAdmin)


class TrackDownloadAdmin(admin.ModelAdmin):
    list_display = ("track", "user", "status", "created_at")
    list_filter = ("track", "user", "status")
    search_fields = ("track__name",)


admin.site.register(models.TrackDownload, TrackDownloadAdmin)


class MediaLikeAdmin(admin.ModelAdmin):
    list_display = ("media", "user", "liked", "created_at")
    list_filter = ("media", "user", "liked")
    search_fields = ("media__name",)


admin.site.register(models.MediaLike, MediaLikeAdmin)

