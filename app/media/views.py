from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter

from core.models import Genre, Track, Media
from media import serializers
from media.tasks import resize_image


class BaseViewSet(viewsets.GenericViewSet,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin):
    """Base viewset for media app"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly, )
    pagination_class = PageNumberPagination
    lookup_field = 'slug'

    def perform_create(self, serializer):
        """Create a new object"""

        serializer.save(user=self.request.user)


class GenreViewSet(BaseViewSet):
    """Manage genres in the database"""

    queryset = Genre.objects.all()
    serializer_class = serializers.GenreSerializer

    def get_queryset(self):
        """Return filtered objects"""

        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )

        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(media__isnull=False).distinct()

        return queryset


class TrackViewSet(BaseViewSet):
    """Manage track in the database"""

    queryset = Track.objects.all()
    serializer_class = serializers.TrackSerializer

    # def get_queryset(self):
    #     """Return objects for the current authenticated user"""
    #
    #     return self.queryset.filter(user=self.request.user)


class MediaViewSet(viewsets.ModelViewSet):
    """Manage media in the database"""

    queryset = Media.objects.all()
    serializer_class = serializers.MediaSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ['title']
    lookup_field = 'slug'

    def perform_create(self, serializer):
        """Create a new object"""

        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""

        if self.action == 'retrieve':
            return serializers.MediaDetailSerializer
        elif self.action == 'image':
            return serializers.MediaImageSerializer

        return self.serializer_class

    @action(methods=['POST'], detail=True, url_path='image')
    def image(self, request, slug=None, version=None,):
        """Upload an image to an media"""

        media = self.get_object()
        serializer = self.get_serializer(
            media,
            data=request.data
        )

        if serializer.is_valid(raise_exception=True):
            serializer.save()

            if media.image:
                resize_image.delay(media.slug, media.image.name)

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def _params_to_slugs(self, qs):
        """Convert a list of string IDs to a list of integers"""

        return [str_id for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieves the media for the current authenticated user"""

        genres = self.request.query_params.get('genres')
        tracks = self.request.query_params.get('tracks')
        queryset = self.queryset

        if genres:
            genre_slugs = self._params_to_slugs(genres)
            queryset = queryset.filter(genres__slug__in=genre_slugs)

        if tracks:
            track_slugs = self._params_to_slugs(tracks)
            queryset = queryset.filter(tracks__slug__in=track_slugs)

        return queryset  # .filter(user=self.request.user)
