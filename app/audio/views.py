from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Genre, Track
from audio import serializers


class GenreViewSet(viewsets.GenericViewSet,
                   mixins.ListModelMixin,
                   mixins.CreateModelMixin):
    """Manage genres in the database"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Genre.objects.all()
    serializer_class = serializers.GenreSerializer

    def perform_create(self, serializer):
        """Create a new genre"""

        serializer.save(user=self.request.user)


class TrackViewSet(viewsets.GenericViewSet,
                   mixins.ListModelMixin,
                   mixins.CreateModelMixin):
    """Manage track in the database"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Track.objects.all()
    serializer_class = serializers.TrackSerializer

    def perform_create(self, serializer):
        """Create a new genre"""

        serializer.save(user=self.request.user)

    # def get_queryset(self):
    #     """Return objects for the current authenticated user"""
    #
    #     return self.queryset.filter(user=self.request.user)
