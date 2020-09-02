from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Genre
from audio import serializers


class GenreViewSet(viewsets.GenericViewSet,
                   mixins.ListModelMixin,
                   mixins.CreateModelMixin):
    """Manage genres in database"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Genre.objects.all()
    serializer_class = serializers.GenreSerializer

    def perform_create(self, serializer):
        """Create a new genre"""

        serializer.save(user=self.request.user)
