from rest_framework.routers import DefaultRouter

from audio import views

app_name = 'audio'

router = DefaultRouter()
router.register('api/genres', views.GenreViewSet, 'genres')
router.register('api/tracks', views.TrackViewSet, 'tracks')
router.register('api/audiobooks', views.AudioBookViewSet, 'audiobooks')
router.register('api/albums', views.AlbumViewSet, 'albums')

urlpatterns = router.urls
