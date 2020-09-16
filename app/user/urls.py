from django.urls import path, re_path, include
from allauth.account.views import confirm_email

app_name = 'user'

urlpatterns = [
    path(r'user/', include('rest_auth.urls')),
    path(r'user/registration/', include('rest_auth.registration.urls')),

    re_path(r'accounts-rest/registration/account-confirm-email/(?P<key>.+)/',
            confirm_email, name='account_confirm_email'),
]
