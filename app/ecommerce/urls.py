from django.urls import path
from .views import HomeView, MediaDetailView, OrderSummaryView, add_to_cart, \
                    remove_from_cart, CheckoutView, PaymentView, AddCouponView

app_name = 'ecommerce'


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('add-to-cart/<slug>', add_to_cart, name='add-to-cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('media/<slug>/', MediaDetailView.as_view(), name='media'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('remove-from-cart/<slug>', remove_from_cart, name='remove-from-cart')
]
