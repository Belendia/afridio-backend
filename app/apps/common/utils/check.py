from django.core.exceptions import ObjectDoesNotExist

from apps.ecommerce.models import OrderMedia, Order


def is_item_already_purchased(request, media):
    try:
        OrderMedia.objects.get(
            media=media,
            user=request.user,
            ordered=True
        )
        return True
    except ObjectDoesNotExist:
        return False


def is_coupon_used_by_current_user(request, coupon):
    coupon_qs = Order.objects.filter(
                user=request.user, coupon__code=coupon.code)

    return coupon_qs.exists()
