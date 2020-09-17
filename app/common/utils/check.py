from django.core.exceptions import ObjectDoesNotExist

from ecommerce.models import OrderMedia


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
