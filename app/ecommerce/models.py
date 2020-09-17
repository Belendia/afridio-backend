from decimal import Decimal

from django.db import models
from django.conf import settings
from django_countries.fields import CountryField
from django.db.models.signals import post_save

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
    ref_code = models.CharField(max_length=120, blank=True, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    medias = models.ManyToManyField(OrderMedia)
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey(
        'Address', related_name='billing_address', on_delete=models.SET_NULL,
        blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        if self.user:
            return f"{ self.user.email }"
        return str(self.ordered_date)

    def get_total(self):
        total = 0
        for order_media in self.medias.all():
            total += order_media.get_final_price()
        if self.coupon:
            total -= Decimal(self.coupon.amount)
        return total


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user:
            return f"{self.user.email}"
        return str(self.timestamp)


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()
    expiry_date = models.DateTimeField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='userprofile',
        on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email


def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)
