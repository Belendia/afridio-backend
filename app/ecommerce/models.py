from django.db import models
from django.conf import settings

from core.models import Media


class OrderMedia(models.Model):
    media = models.ForeignKey(Media, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{ self.media.title }"

    def get_total_item_price(self):
        return 1 * self.media.price

    def get_total_discount_item_price(self):
        return 1 * self.media.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - \
               self.get_total_discount_item_price()

    def get_final_price(self):
        if self.media.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):

    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    medias = models.ManyToManyField(OrderMedia)
    ordered = models.BooleanField(default=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{ self.user.email }"

    def get_total(self):
        total = 0
        for order_media in self.medias.all():
            total += order_media.get_final_price()
        # if self.coupon:
        #     total -= self.coupon.amount
        return total

