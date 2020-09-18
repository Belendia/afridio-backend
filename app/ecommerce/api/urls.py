from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import OrderListView, AddToCartView, OrderDetailView, \
    PaymentView, AddCouponView, AddressViewSet, CountryListView, \
    OrderMediaDeleteView

app_name = 'ecommerce-api'

router = DefaultRouter()

router.register('addresses', AddressViewSet, 'address')

urlpatterns = [
    path('shop/order/', OrderListView.as_view(), name='orders'),
    path('shop/cart/', AddToCartView.as_view(), name='add-to-cart'),
    path('shop/cart/<slug>/', OrderMediaDeleteView.as_view(),
         name='remove-from-cart'),
    path('shop/order/summary/', OrderDetailView.as_view(),
         name='order-summary'),
    path('shop/checkout/', PaymentView.as_view(), name='checkout'),
    path('shop/coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('countries/', CountryListView.as_view(), name='country-list'),
]

urlpatterns += router.urls
