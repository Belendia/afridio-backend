from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Genre, Track, AudioBook, Album
from audio import serializers


class BaseViewSet(viewsets.GenericViewSet,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin):
    """Base viewset for audio app"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        """Create a new object"""

        serializer.save(user=self.request.user)


class GenreViewSet(BaseViewSet):
    """Manage genres in the database"""

    queryset = Genre.objects.all()
    serializer_class = serializers.GenreSerializer


class TrackViewSet(BaseViewSet):
    """Manage track in the database"""

    queryset = Track.objects.all()
    serializer_class = serializers.TrackSerializer

    # def get_queryset(self):
    #     """Return objects for the current authenticated user"""
    #
    #     return self.queryset.filter(user=self.request.user)


class AudioBookViewSet(viewsets.ModelViewSet):
    """Manage audiobooks in the database"""

    queryset = AudioBook.objects.all()
    serializer_class = serializers.AudioBookSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        """Create a new object"""

        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""

        if self.action == 'retrieve':
            return serializers.AudioBookDetailSerializer
        elif self.action == 'image':
            return serializers.AlbumImageSerializer

        return self.serializer_class

    @action(methods=['POST'], detail=True, url_path='image')
    def image(self, request, pk=None):
        """Upload an image to an album"""

        audiobook = self.get_object()
        serializer = self.get_serializer(
            audiobook,
            data=request.data
        )

        if serializer.is_valid():
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
    #     """Retrieves the audiobooks for the current authenticated user"""
    #
    #     return self.queryset.filter(user=self.request.user)


class AlbumViewSet(viewsets.ModelViewSet):
    """Manage albums in the database"""

    queryset = Album.objects.all()
    serializer_class = serializers.AlbumSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        """Create a new object"""

        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""

        if self.action == 'retrieve':
            return serializers.AlbumDetailSerializer
        elif self.action == 'image':
            return serializers.AlbumImageSerializer

        return self.serializer_class

    @action(methods=['POST'], detail=True, url_path='image')
    def image(self, request, pk=None):
        """Upload an image to an album"""

        album = self.get_object()
        serializer = self.get_serializer(
            album,
            data=request.data
        )

        if serializer.is_valid():
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
    #     """Retrieves the albums for the current authenticated user"""
    #
    #     return self.queryset.filter(user=self.request.user)
