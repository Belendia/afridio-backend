from django.urls import path
from .views import HomeView, MediaDetailView, OrderSummaryView, add_to_cart, \
                    remove_from_cart

app_name = 'ecommerce'


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('media/<slug>/', MediaDetailView.as_view(), name='media'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('add-to-cart/<slug>', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>', remove_from_cart, name='remove-from-cart')
]
