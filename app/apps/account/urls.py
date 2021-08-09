from django.urls import path, re_path, include

from apps.account.views import LoginView, RegisterUserView, MeView, LogoutView, UpdateUserView

app_name = 'account'

urlpatterns = [
    path(r'user/register/', RegisterUserView.as_view(), name='create'),
    path(r'user/login/', LoginView.as_view(), name='token'),
    path(r'user/me/', MeView.as_view(), name='me'),
    path(r'user/logout/', LogoutView.as_view(), name='logout'),
    path(r'user/update/', UpdateUserView.as_view(), name='update'),
]
