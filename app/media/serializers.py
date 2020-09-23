from rest_framework import serializers

from core.models import Genre, Track, Media

from common.utils.validators import validate_image_size, validate_file_type


class GenreSerializer(serializers.ModelSerializer):
    """Serializer for genre objects"""

    class Meta:
        model = Genre
        fields = ('slug', 'name', 'created', 'updated')
        read_only_fields = ('id', 'slug', 'created', 'updated')
        lookup_field = 'slug'


class TrackSerializer(serializers.ModelSerializer):
    """Serializer for track objects"""
    media_list = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Media.objects.all()
    )

    class Meta:
        model = Track
        fields = ('slug', 'name', 'popularity', 'file_url',
                  'duration_ms', 'created', 'updated', 'media_list')
        read_only_fields = ('id', 'slug', 'file_url', 'created', 'updated')
        lookup_field = 'slug'


class TrackFileSerializer(serializers.ModelSerializer):
    """Serializer for uploading media file to track"""

    file_url = serializers.FileField(validators=[validate_file_type])

    class Meta:
        model = Media
        fields = ('slug', 'file_url')
        read_only_fields = ('slug', )
        lookup_field = 'slug'


class MediaSerializer(serializers.ModelSerializer):
    """Serializer for media objects"""

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
        model = Media
        fields = ('title', 'price', 'discount_price', 'image', 'slug',
                  'estimated_length_in_seconds', 'popularity', 'release_date',
                  'media_format', 'word_count', 'album_type', 'genres',
                  'tracks', 'created', 'updated')
        read_only_fields = ('id', 'slug', 'created', 'updated')
        lookup_field = 'slug'


class MediaDetailSerializer(MediaSerializer):
    """Serializer an media detail"""

    genres = GenreSerializer(many=True, read_only=True)
    tracks = TrackSerializer(many=True, read_only=True)


class MediaImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to media"""

    image = serializers.ImageField(validators=[validate_image_size])

    class Meta:
        model = Media
        fields = ('slug', 'image')
        read_only_fields = ('slug', )
        lookup_field = 'slug'
