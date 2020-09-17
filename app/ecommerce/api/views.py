from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from ecommerce.models import Order, OrderMedia
from core.models import Media
from ecommerce.api.serializers import OrderSerializer

from common.utils.check import is_item_already_purchased


class OrderListView(ListAPIView):
    pass


class AddToCartView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        slug = request.data.get('slug', None)
        if slug is None:
            return Response({"detail": "Invalid request"},
                            status=HTTP_400_BAD_REQUEST)

        media = get_object_or_404(Media, slug=slug)

        if is_item_already_purchased(request, media):
            return Response({"detail": "You already purchased this item"},
                            status=HTTP_400_BAD_REQUEST)

        order_media, created = OrderMedia.objects.get_or_create(
            media=media,
            user=request.user,
            ordered=False
        )
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            # check if the order media is in the order
            if order.medias.filter(media__slug=media.slug).exists():
                return Response({"detail": "This item is in the cart."},
                                status=HTTP_400_BAD_REQUEST)
            else:
                order.medias.add(order_media)
                return Response(status=HTTP_200_OK)
        else:
            ordered_date = timezone.now()
            order = Order.objects.create(
                user=request.user, ordered_date=ordered_date)
            order.medias.add(order_media)
            return Response(status=HTTP_200_OK)


class OrderDetailView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            return order
        except ObjectDoesNotExist:
            raise Http404("You do not have an active order")
