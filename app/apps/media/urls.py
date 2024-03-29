# from rest_framework.routers import DefaultRouter
from django.urls import path, include

from rest_framework_nested import routers
from apps.media import views

app_name = 'media'

# router = DefaultRouter()
router = routers.SimpleRouter()

# /genres
router.register('genres', views.GenreViewSet, 'genres')
# /medias
router.register('medias', views.MediaViewSet, 'medias')
# /tracks
router.register('tracks', views.TrackViewSet, 'tracks')
# /home
router.register('home', views.HomeAPIView, 'home')
# /searchby
router.register('searchby', views.SearchByAPIView, 'searchby')

# /medias/:media_slug/tracks
tracks_router = routers.NestedSimpleRouter(router, r'medias', lookup='media')
tracks_router.register(r'tracks', views.TrackNestedViewSet, basename='media_tracks')

# /medias/:media_slug/like
like_router = routers.NestedSimpleRouter(router, r'medias', lookup='media')
like_router.register(r'like', views.MediaLikeNestedViewSet, basename='media_like')

# /tracks/:track_slug/download
download_router = routers.NestedSimpleRouter(router, r'tracks', lookup='track')
download_router.register(r'download', views.TrackDownloadNestedViewSet, basename='track_download')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(tracks_router.urls)),
    path('', include(download_router.urls)),
    path('', include(like_router.urls)),
]
