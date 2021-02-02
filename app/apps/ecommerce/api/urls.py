from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import AddToCartView, OrderDetailView, CheckoutView, \
    AddCouponView, AddressViewSet, CountryListView, OrderMediaDeleteView, \
    PaymentListView

app_name = 'ecommerce-api'

router = DefaultRouter()

router.register('addresses', AddressViewSet, 'addresses')

urlpatterns = [
    path('cart/', AddToCartView.as_view(), name='add-to-cart'),
    path('cart/<slug>/', OrderMediaDeleteView.as_view(),
         name='remove-from-cart'),
    path('order/', OrderDetailView.as_view(),
         name='order-summary'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('countries/', CountryListView.as_view(), name='country-list'),
    path('payments/', PaymentListView.as_view(), name='payments-list')
]

urlpatterns += router.urls
