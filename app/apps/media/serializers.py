from rest_framework import serializers

from apps.media.models import Genre, Track, Media

from apps.common.utils.validators import validate_image_size, validate_file_type


class GenreSerializer(serializers.ModelSerializer):
    """Serializer for genre objects"""

    class Meta:
        model = Genre
        fields = ('slug', 'name', 'created', 'updated')
        read_only_fields = ('id', 'slug', 'created', 'updated')
        lookup_field = 'slug'


class GenreDisplaySerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('slug', 'name')


class TrackSerializer(serializers.ModelSerializer):
    """Serializer for track objects"""

    medias = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Media.objects.all()
    )
    media_detail = serializers.SerializerMethodField()

    class Meta:
        model = Track
        fields = ('slug', 'name', 'popularity', 'file_url',
                  'duration_ms', 'created', 'updated', 'medias',
                  'media_detail')
        read_only_fields = ('id', 'slug', 'file_url', 'created', 'updated')
        lookup_field = 'slug'

    def get_media_detail(self, obj):
        return TrackMediasDisplaySerializer(obj.medias.all(),
                                            many=True).data


class TrackMediasDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = (
            'slug',
            'title'
        )
        read_only_fields = ('title', )


class TrackFileSerializer(serializers.ModelSerializer):
    """Serializer for uploading media file to track"""

    file_url = serializers.FileField(validators=[validate_file_type])

    class Meta:
        model = Media
        fields = ('slug', 'file_url')
        read_only_fields = ('slug', )
        lookup_field = 'slug'


class MediaTracksDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = (
            'slug',
            'name',
            'file_url'
        )
        read_only_fields = ('name', 'file_url')


class MediaSerializer(serializers.ModelSerializer):
    """Serializer for media objects"""

    genres = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )
    genres_detail = serializers.SerializerMethodField()

    tracks = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Track.objects.all()
    )
    tracks_detail = serializers.SerializerMethodField()

    class Meta:
        model = Media
        fields = ('title', 'price', 'discount_price', 'image', 'slug',
                  'estimated_length_in_seconds', 'popularity', 'release_date',
                  'media_format', 'word_count', 'album_type', 'genres',
                  'genres_detail', 'tracks', 'tracks_detail', 'created',
                  'updated')
        read_only_fields = ('id', 'slug', 'created', 'updated')
        lookup_field = 'slug'

    def get_genres_detail(self, obj):
        return GenreDisplaySerializer(obj.genres.all(), many=True).data

    def get_tracks_detail(self, obj):
        return MediaTracksDisplaySerializer(obj.tracks.all(), many=True).data


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
