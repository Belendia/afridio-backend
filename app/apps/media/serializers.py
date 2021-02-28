from rest_framework import serializers

from apps.media.models import Genre, Track, Media

from apps.common.utils.validators import validate_image_size, validate_file_type


class GenreSerializer(serializers.ModelSerializer):
    """Serializer for genre objects"""

    class Meta:
        model = Genre
        fields = ('slug', 'name')
        read_only_fields = ('id', 'slug')
        lookup_field = 'slug'


class GenreDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', )


class TrackSerializer(serializers.ModelSerializer):
    """Serializer for track objects"""

    medias = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Media.objects.all()
    )

    class Meta:
        model = Track
        fields = ('slug', 'name', 'popularity', 'file_url', 'sample',
                  'duration_ms',  'medias')
        read_only_fields = ('id', 'slug', 'file_url')
        lookup_field = 'slug'


class TrackFileSerializer(serializers.ModelSerializer):
    """Serializer for uploading media file to track"""

    file_url = serializers.FileField(validators=[validate_file_type])

    class Meta:
        model = Media
        fields = ('slug', 'file_url')
        read_only_fields = ('slug',)
        lookup_field = 'slug'


class TracksDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = (
            'name',
            'file_url'
        )
        read_only_fields = ('name', 'file_url')


class MediaSerializer(serializers.ModelSerializer):
    """Serializer for media objects"""

    genre_list = serializers.SerializerMethodField()
    genres = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )

    tracks = serializers.SerializerMethodField()

    class Meta:
        model = Media
        fields = ('title', 'price', 'discount_price', 'image', 'slug',
                  'estimated_length_in_seconds', 'rating', 'release_date',
                  'media_format', 'word_count', 'album_type', 'authors', 'genres', 'genre_list',
                  'tracks')
        read_only_fields = ('id', 'slug')
        lookup_field = 'slug'

    def get_genre_list(self, obj):
        return GenreDisplaySerializer(obj.genres.all(), many=True).data

    def get_tracks(self, obj):
        return TracksDisplaySerializer(obj.tracks.filter(sample=True), many=True).data


class MediaDetailSerializer(MediaSerializer):
    """Serializer an media detail"""

    genres = GenreDisplaySerializer(many=True, read_only=True)
    tracks = TracksDisplaySerializer(many=True, read_only=True)


class MediaImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to media"""

    image = serializers.ImageField(validators=[validate_image_size])
    result = serializers.SerializerMethodField()

    class Meta:
        model = Media
        fields = ('image', 'result')

    def get_result(self, obj):
        return 'Processing image'

