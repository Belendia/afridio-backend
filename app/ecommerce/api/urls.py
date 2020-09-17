from django.urls import path
from .views import OrderListView, AddToCartView, OrderDetailView, \
    PaymentView, AddCouponView

urlpatterns = [
    path('shop/order/', OrderListView.as_view(), name='orders'),
    path('shop/cart/', AddToCartView.as_view(), name='add-to-cart'),
    path('shop/order/summary/', OrderDetailView.as_view(),
         name='order-summary'),
    path('shop/checkout/', PaymentView.as_view(), name='checkout'),
    path('shop/coupon/', AddCouponView.as_view(), name='ass-coupon'),
]
