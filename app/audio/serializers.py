from rest_framework import serializers

from core.models import Genre, Track, AudioBook, Album


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


class AudioBookSerializer(serializers.ModelSerializer):
    """Serializer for audiobook objects"""

    genres = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Genre.objects.all()
    )
    tracks = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Track.objects.all()
    )

    class Meta:
        model = AudioBook
        fields = ('id', 'title', 'word_count', 'estimated_length_in_seconds',
                  'price', 'slug', 'created', 'updated', 'genres', 'tracks')
        read_only_fields = ('id', 'slug', 'created', 'updated')


class AudioBookDetailSerializer(AudioBookSerializer):
    """Serializer an audiobook detail"""

    genres = GenreSerializer(many=True, read_only=True)
    tracks = TrackSerializer(many=True, read_only=True)


class AlbumSerializer(serializers.ModelSerializer):
    """Serializer for album objects"""

    genres = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Genre.objects.all()
    )
    tracks = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Track.objects.all()
    )

    class Meta:
        model = Album
        fields = ('id', 'name', 'album_type', 'estimated_length_in_seconds',
                  'popularity', 'price', 'release_date', 'slug', 'created',
                  'updated', 'genres', 'tracks')
        read_only_fields = ('id', 'slug', 'created', 'updated')


class AlbumDetailSerializer(AlbumSerializer):
    """Serializer an album detail"""

    genres = GenreSerializer(many=True, read_only=True)
    tracks = TrackSerializer(many=True, read_only=True)
