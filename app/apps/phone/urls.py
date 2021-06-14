from django.urls import path
from rest_framework import routers

from . import views

router = routers.SimpleRouter()

# router.register(r'phones', views.PhoneViewset)

urlpatterns = [
    # path('send_sms_code/', views.SendSMS.as_view(), name='send_sms_code'),
    path(r'phone/verify/', views.VerifyPhoneNumberANDLoginViewSet.as_view(),
         name='verify'),
    path(r'phone/resend/', views.ResendOTPViewSet.as_view(),
         name='resend'),
]

urlpatterns += router.urls
