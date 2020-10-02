from django.urls import path
from rest_framework import routers

from . import views

router = routers.SimpleRouter()

router.register(r'phones', views.PhoneViewset)

urlpatterns = [
    path('send_sms_code/', views.send_sms, name='send_sms_code'),
    path('verify_phone/<int:sms_code>', views.verify_phone,
         name='verify_phone'),
]

urlpatterns += router.urls
