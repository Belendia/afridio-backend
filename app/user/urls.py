from django.urls import path, re_path, include
from allauth.account.views import confirm_email

from user.api.views import FacebookLogin
from user.views import CreateTokenView, CreateUserView

app_name = 'user'

urlpatterns = [
    path(r'user/', include('rest_auth.urls')),
    # path(r'user/registration/', include('rest_auth.registration.urls')),
    path(r'user/register/', CreateUserView.as_view(), name='create'),
    path(r'user/facebook/', FacebookLogin.as_view(), name='fb_login'),
    path(r'user/phone/login/', CreateTokenView.as_view(), name='token'),
    re_path(r'accounts-rest/registration/account-confirm-email/(?P<key>.+)/',
            confirm_email, name='account_confirm_email'),
]
