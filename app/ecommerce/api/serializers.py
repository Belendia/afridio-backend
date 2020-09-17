from rest_framework import serializers
from ecommerce.models import Order, OrderMedia, Coupon

from audio.serializers import MediaSerializer


class StringSerializer(serializers.StringRelatedField):
    def to_internal_value(self, value):
        return value


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = (
            'slug',
            'code',
            'amount'
        )


class OrderMediaSerializer(serializers.ModelSerializer):
    media = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderMedia
        fields = (
            'media',
            'final_price'
        )

    def get_media(self, obj):
        return MediaSerializer(obj.media).data

    def get_final_price(self, obj):
        return obj.get_final_price()


class OrderSerializer(serializers.ModelSerializer):
    order_medias = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    coupon = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'ordered_date',
            'order_medias',
            'total',
            'coupon'
        )

    def get_order_medias(self, obj):
        return OrderMediaSerializer(obj.medias.all(), many=True).data

    def get_total(self, obj):
        return obj.get_total()

    def get_coupon(self, obj):
        if obj.coupon is not None:
            return CouponSerializer(obj.coupon).data
        return None
