from django.urls import path, re_path, include

from user.views import CreateTokenView, CreateUserView, ManageUserView

app_name = 'user'

urlpatterns = [
    path(r'user/register/', CreateUserView.as_view(), name='create'),
    path(r'user/login/', CreateTokenView.as_view(), name='token'),
    path('user/me/', ManageUserView.as_view(), name='me'),
]
