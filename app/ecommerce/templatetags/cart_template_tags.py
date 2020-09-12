from django import template
from ecommerce.models import Order

register = template.Library()


@register.filter
def cart_media_count(user):
    if user.is_authenticated:
        qs = Order.objects.filter(user=user, ordered=False)
        if qs.exists():
            return qs[0].medias.count()
    return 0
