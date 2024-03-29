import stripe
from secrets import token_urlsafe
from django_countries import countries

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import viewsets
from rest_framework.generics import ListAPIView, RetrieveAPIView, \
    DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from apps.ecommerce.models import Order, OrderMedia, Payment, UserProfile, Coupon, \
    Address
from apps.media.models import Media
from apps.ecommerce.api.serializers import OrderSerializer, AddressSerializer, \
    PaymentSerializer

from apps.common.utils.check import is_item_already_purchased, \
    is_coupon_used_by_current_user

stripe.api_key = settings.STRIPE_SECRET_KEY


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


class OrderMediaDeleteView(DestroyAPIView):
    permission_classes = (IsAuthenticated, )
    lookup_field = 'slug'

    def get_queryset(self):
        return OrderMedia.objects.all().filter(user=self.request.user)


class OrderDetailView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            return order
        except ObjectDoesNotExist:
            raise Http404("You do not have an active order")


class CheckoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        userprofile = UserProfile.objects.get(user=self.request.user)

        token = request.data.get('stripeToken')

        billing_address_id = request.data.get('billing_address')
        billing_address = Address.objects.get(slug=billing_address_id)

        if userprofile.stripe_customer_id != '' and \
                userprofile.stripe_customer_id is not None:
            customer = stripe.Customer.retrieve(
                userprofile.stripe_customer_id)
            customer.sources.create(source=token)

        else:
            customer = stripe.Customer.create(
                email=self.request.user.email,
            )
            customer.sources.create(source=token)
            userprofile.stripe_customer_id = customer['id']
            userprofile.one_click_purchasing = True
            userprofile.save()

        amount = int(order.get_total() * 100)

        try:
            charge = stripe.Charge.create(
                amount=amount,  # cents
                currency="usd",
                customer=userprofile.stripe_customer_id
            )

            # create the payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            # assign the payment to the order

            order_medias = order.medias.all()
            order_medias.update(ordered=True)
            for item in order_medias:
                item.save()

            order.ordered = True
            order.payment = payment
            order.billing_address = billing_address
            order.ref_code = token_urlsafe(32)
            order.save()

            return Response(status=HTTP_200_OK)

        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            return Response({"detail": f"{err.get('message')}"},
                            status=HTTP_400_BAD_REQUEST)

        except stripe.error.RateLimitError:
            # Too many requests made to the API too quickly
            return Response({"detail": "Rate limit error"},
                            status=HTTP_400_BAD_REQUEST)

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            print(e)
            return Response({"detail": "Invalid parameters"},
                            status=HTTP_400_BAD_REQUEST)

        except stripe.error.AuthenticationError:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            return Response({"detail": "Not authenticated"},
                            status=HTTP_400_BAD_REQUEST)

        except stripe.error.APIConnectionError:
            # Network communication with Stripe failed
            return Response({"detail": "Network error"},
                            status=HTTP_400_BAD_REQUEST)

        except stripe.error.StripeError:
            # Display a very generic error to the account, and maybe send
            # yourself an email
            return Response({"detail": "Something went wrong. You were not "
                                       "charged. Please try again."},
                            status=HTTP_400_BAD_REQUEST)

        except Exception:
            # send an email to ourselves

            return Response({"detail": "A serious error occurred. We have "
                                       "been notified."},
                            status=HTTP_400_BAD_REQUEST)

        return Response({"detail": "Invalid data received"},
                        status=HTTP_400_BAD_REQUEST)


class AddCouponView(APIView):
    def post(self, request, *args, **kwargs):
        code = request.data.get('code', None)
        if code is None:
            return Response({"detail": "Invalid data received"},
                            status=HTTP_400_BAD_REQUEST)
        order = Order.objects.get(
            user=self.request.user, ordered=False)
        coupon = get_object_or_404(Coupon, code=code)

        if timezone.now() > coupon.expiry_date:
            return Response({"detail": "This coupon has expired"},
                            status=HTTP_400_BAD_REQUEST)

        if is_coupon_used_by_current_user(self.request, coupon):
            return Response({"detail": "This coupon has been used"},
                            status=HTTP_400_BAD_REQUEST)

        order.coupon = coupon
        order.save()
        return Response(status=HTTP_200_OK)


class AddressViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = AddressSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return Address.objects.all().filter(user=self.request.user)

    def perform_create(self, serializer):
        """Create a new object"""

        serializer.save(user=self.request.user)


class CountryListView(APIView):
    def get(self, request, *args, **kwargs):
        return Response(countries, status=HTTP_200_OK)


class PaymentListView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)
