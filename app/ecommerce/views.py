from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone

from core.models import Media
from ecommerce.models import Order, OrderMedia


class HomeView(ListView):

    queryset = Media.objects.filter(media_format='AUDIOBOOK')
    template_name = "home.html"


class MediaDetailView(DetailView):

    model = Media
    template_name = "media.html"


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")


@login_required
def add_to_cart(request, slug):
    media = get_object_or_404(Media, slug=slug)
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
            messages.info(request, "This item is in the cart.")
            return redirect("ecommerce:order-summary")
        else:
            order.medias.add(order_media)
            messages.info(request, "This item was added to your cart.")
            return redirect("ecommerce:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.medias.add(order_media)
        messages.info(request, "This item was added to your cart.")
        return redirect("ecommerce:order-summary")


@login_required
def remove_from_cart(request, slug):
    media = get_object_or_404(Media, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.medias.filter(media__slug=media.slug).exists():
            order_media = OrderMedia.objects.filter(
                media=media,
                user=request.user,
                ordered=False
            )[0]
            order.medias.remove(order_media)
            order_media.delete()
            messages.info(request, "This item was removed from your cart.")
            return redirect("ecommerce:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("ecommerce:media", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("ecommerce:media", slug=slug)
