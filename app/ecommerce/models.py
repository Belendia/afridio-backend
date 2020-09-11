from django.db import models
from django.conf import settings

from core.models import Media


class OrderMedia(models.Model):
    media = models.ForeignKey(Media, on_delete=models.CASCADE)


class Order(models.Model):

    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    medias = models.ManyToManyField(OrderMedia)
    ordered = models.BooleanField(default=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )
