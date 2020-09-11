from django.urls import path
from .views import media_list, order_summary


app_name = 'ecommerce'


urlpatterns = [
    path('', media_list, name='media-list'),
    path('order_summary', order_summary, name='order-summary'),
]
