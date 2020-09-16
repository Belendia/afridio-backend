from django.urls import path, re_path, include
from allauth.account.views import confirm_email

from user.api.views import FacebookLogin

app_name = 'user'

urlpatterns = [
    path(r'user/', include('rest_auth.urls')),
    path(r'user/registration/', include('rest_auth.registration.urls')),
    path(r'user/facebook/', FacebookLogin.as_view(), name='fb_login'),

    re_path(r'accounts-rest/registration/account-confirm-email/(?P<key>.+)/',
            confirm_email, name='account_confirm_email'),
]
