from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly, \
    IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from apps.media.models import Genre, Track, Media, Format
from apps.media import serializers


# from apps.media.tasks.encode_track_task import encode_track


class BaseViewSet(viewsets.GenericViewSet,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin):
    """Base viewset for media app"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)
    pagination_class = PageNumberPagination
    lookup_field = 'slug'

    def perform_create(self, serializer):
        """Create a new object"""

        serializer.save(user=self.request.user)


# /genres
class GenreViewSet(BaseViewSet):
    """Manage genres in the database"""

    queryset = Genre.objects.all()
    serializer_class = serializers.GenreSerializer

    # def get_queryset(self):
    #     """Return filtered objects"""
    #
    #     assigned_only = bool(
    #         int(self.request.query_params.get('assigned_only', 0))
    #     )
    #
    #     queryset = self.queryset
    #     if assigned_only:
    #         queryset = queryset.filter(media__isnull=False).distinct()
    #
    #     return queryset


# /tracks
class TrackViewSet(BaseViewSet):
    """Manage track in the database"""

    queryset = Track.objects.all()
    serializer_class = serializers.TrackSerializer

    def get_serializer_class(self):
        """Return appropriate serializer class"""

        if self.action == 'file':
            return serializers.TrackFileSerializer

        return self.serializer_class

    @action(methods=['POST'], detail=True, url_path='file')
    def file(self, request, slug=None, version=None, ):
        """Upload a media file to a track"""

        track = self.get_object()
        serializer = self.get_serializer(
            track,
            data=request.data
        )

        if serializer.is_valid(raise_exception=True):
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    # def get_queryset(self):
    #     """Return objects for the current authenticated account"""
    #
    #     return self.queryset.filter(account=self.request.account)


# /medias
class MediaViewSet(viewsets.ModelViewSet):
    """Manage media in the database"""

    queryset = Media.objects.filter(status=Media.StatusType.PUBLISHED)
    serializer_class = serializers.MediaSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ['title']
    lookup_field = 'slug'

    def perform_create(self, serializer):
        """Create a new object"""

        serializer.save(user=self.request.user)

    # def get_serializer_class(self):
    #     """Return appropriate serializer class"""
    #
    #     # if self.action == 'retrieve':
    #     #     return serializers.MediaDetailSerializer
    #     if self.action == 'image':
    #         return serializers.MediaImageSerializer
    #
    #     return self.serializer_class

    # @action(methods=['POST'], detail=True, url_path='image')
    # def image(self, request, slug=None, version=None, ):
    #     """Upload an image to an media"""
    #
    #     media = self.get_object()
    #     serializer = self.get_serializer(
    #         media,
    #         data=request.data
    #     )
    #
    #     if serializer.is_valid(raise_exception=True):
    #         serializer.save()
    #
    #         if media.image:
    #             resize_image.delay(media.slug, media.image.name)
    #
    #         return Response(
    #             serializer.data,
    #             status=status.HTTP_200_OK
    #         )
    #
    #     return Response(
    #         serializer.errors,
    #         status=status.HTTP_400_BAD_REQUEST
    #     )

    def _params_to_slugs(self, qs):
        """Convert a list of string IDs to a list of integers"""

        return [str_id for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieves the media for the current authenticated account"""
        genres = self.request.query_params.get('genres')
        tracks = self.request.query_params.get('tracks')
        category = self.request.query_params.get('category')
        queryset = self.queryset

        if genres:
            genre_slugs = self._params_to_slugs(genres)
            queryset = queryset.filter(genres__slug__in=genre_slugs)

        if tracks:
            track_slugs = self._params_to_slugs(tracks)
            queryset = queryset.filter(tracks__slug__in=track_slugs)

        if category:
            queryset = queryset.filter(media_format__slug=category)

        return queryset  # .filter(account=self.request.account)


# /medias/:media_slug/tracks
class TrackNestedViewSet(viewsets.ViewSet):
    pagination_class = None
    permission_classes = (IsAuthenticated, DjangoModelPermissionsOrAnonReadOnly)
    queryset = Track.objects.all()
    serializer_class = serializers.TrackSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(medias__slug=kwargs['media_slug'])
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        try:
            # check that the slug passed in the route exists in the database
            media = Media.objects.get(slug=kwargs['media_slug'])
            # assign the slug to medias in the request
            request.data['medias'] = [media.slug, ]
            # assign the track data in the class's serializer
            serializer = self.serializer_class(data=request.data)
            # validate the track data
            serializer.is_valid(raise_exception=True)
            # save the track data
            serializer.save(user=self.request.user)
        except Exception as e:
            return Response({"detail": str(e)},
                            status=HTTP_400_BAD_REQUEST)
        return Response(status=HTTP_201_CREATED)


# /home
class HomeAPIView(viewsets.ViewSet):
    """Custom queryset api view. Does not implement pagination"""

    pagination_class = None
    permission_classes = (IsAuthenticated,)
    slice_size = 5  # count limit for each of the source queries
    featured_size = 5  # count limit for featured medias

    def list(self, request, *args, **kwargs):
        queryset = Media.objects.all()
        home_response = []

        # Featured media
        f = {'id': 'featured', 'title': 'Featured'}
        qs = queryset.filter(featured=True, status=Media.StatusType.PUBLISHED).order_by('-created_at')[:self.featured_size]
        if qs.count():
            serializer = serializers.MediaSerializer(qs, many=True)
            f["medias"] = serializer.data
        home_response.append(f)

        # Media by format
        format_qs = Format.objects.all().order_by('sequence')
        for format in format_qs:

            qs = queryset.filter(media_format=format.id, status=Media.StatusType.PUBLISHED).order_by('-created_at')[:self.slice_size]
            if qs.count():
                f = {'id': format.slug, 'title': format.name}
                serializer = serializers.MediaSerializer(qs, many=True)
                f["medias"] = serializer.data
                home_response.append(f)

        return Response(home_response)
