from django.urls import path, re_path, include

from user.views import CreateTokenView, CreateUserView

app_name = 'user'

urlpatterns = [
    path(r'user/register/', CreateUserView.as_view(), name='create'),
    path(r'user/login/', CreateTokenView.as_view(), name='token'),
]
