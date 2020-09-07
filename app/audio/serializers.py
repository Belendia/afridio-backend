from rest_framework import serializers

from core.models import Genre, Track, AudioBook, Album


class GenreSerializer(serializers.ModelSerializer):
    """Serializer for genre objects"""

    class Meta:
        model = Genre
        fields = ('slug', 'name', 'created', 'updated')
        read_only_fields = ('id', 'slug', 'created', 'updated')
        lookup_field = 'slug'


class TrackSerializer(serializers.ModelSerializer):
    """Serializer for track objects"""

    class Meta:
        model = Track
        fields = ('slug', 'name', 'popularity', 'original_url',
                  'duration_ms', 'created', 'updated')
        read_only_fields = ('id', 'slug', 'original_url', 'created', 'updated')
        lookup_field = 'slug'


class AudioBookSerializer(serializers.ModelSerializer):
    """Serializer for audiobook objects"""

    genres = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )
    tracks = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Track.objects.all()
    )

    class Meta:
        model = AudioBook
        fields = ('slug', 'title', 'word_count', 'estimated_length_in_seconds',
                  'price', 'image', 'created', 'updated', 'genres', 'tracks')
        read_only_fields = ('id', 'slug', 'created', 'updated')
        lookup_field = 'slug'


class AudioBookDetailSerializer(AudioBookSerializer):
    """Serializer an audiobook detail"""

    genres = GenreSerializer(many=True, read_only=True)
    tracks = TrackSerializer(many=True, read_only=True)


class AlbumSerializer(serializers.ModelSerializer):
    """Serializer for album objects"""

    genres = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )
    tracks = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Track.objects.all()
    )

    class Meta:
        model = Album
        fields = ('slug', 'name', 'album_type', 'estimated_length_in_seconds',
                  'popularity', 'price', 'release_date', 'image', 'created',
                  'updated', 'genres', 'tracks')
        read_only_fields = ('id', 'slug', 'created', 'updated')
        lookup_field = 'slug'


class AlbumDetailSerializer(AlbumSerializer):
    """Serializer an album detail"""

    genres = GenreSerializer(many=True, read_only=True)
    tracks = TrackSerializer(many=True, read_only=True)


class AudioBookImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to audio books"""

    class Meta:
        model = AudioBook
        fields = ('slug', 'image')
        read_only_fields = ('slug', )
        lookup_field = 'slug'


class AlbumImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to albums"""

    class Meta:
        model = Album
        fields = ('slug', 'image')
        read_only_fields = ('slug', )
        lookup_field = 'slug'
