from rest_framework import serializers

from core.models import Genre


class GenreSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Genre
        fields = ('id', 'name')
        read_only_fields = ('id',)
