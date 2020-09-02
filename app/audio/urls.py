from django.urls import path, include
from rest_framework.routers import DefaultRouter

from audio import views


router = DefaultRouter()
router.register('genres', views.GenreViewSet)

app_name = 'audio'

urlpatterns = [
    path('', include(router.urls))
]
