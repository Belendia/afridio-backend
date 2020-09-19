from rest_framework.routers import DefaultRouter

from media import views

app_name = 'media'

router = DefaultRouter()
router.register('genres', views.GenreViewSet, 'genres')
router.register('tracks', views.TrackViewSet, 'tracks')
router.register('medias', views.MediaViewSet, 'medias')

urlpatterns = router.urls
