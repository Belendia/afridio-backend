from rest_framework import serializers

from core.models import Genre, Track


class GenreSerializer(serializers.ModelSerializer):
    """Serializer for genre objects"""

    class Meta:
        model = Genre
        fields = ('id', 'name', 'slug', 'created', 'updated')
        read_only_fields = ('id', 'slug', 'created', 'updated')


class TrackSerializer(serializers.ModelSerializer):
    """Serializer for track objects"""

    class Meta:
        model = Track
        fields = ('id', 'name', 'popularity', 'original_url',
                  'duration_ms', 'slug', 'created', 'updated')
        read_only_fields = ('id', 'slug', 'original_url', 'created', 'updated')
