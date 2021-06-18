from rest_framework import serializers

from apps.media.models import Genre, Track, Media, Language, Format, Author

from apps.common.utils.validators import validate_image_size, validate_file_type


# Genre Serializers
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
        fields = ('name',)


# Language Serializers
class LanguageSerializer(serializers.ModelSerializer):
    """Serializer for language objects"""

    class Meta:
        model = Language
        fields = ('name',)
        read_only_fields = ('id',)
        lookup_field = 'id'


class LanguageDisplayField(serializers.RelatedField):
    def to_representation(self, value):
        return value.name

    def get_queryset(self):

        return Language.objects.filter(
            slug=self.kwargs['slug'],
        )

    def to_internal_value(self, value):
        language = None
        try:
            language = Language.objects.get(
                slug=value,
            )
        except:
            raise serializers.ValidationError("Language not found.")

        return language


# Media format serializers
class FormatSerializer(serializers.ModelSerializer):
    """Serializer for media format objects"""

    class Meta:
        model = Format
        fields = ('name',)
        read_only_fields = ('id',)
        lookup_field = 'slug'


class FormatDisplayField(serializers.RelatedField):
    def to_representation(self, value):
        return value.name

    def get_queryset(self):

        return format.objects.filter(
            slug=self.kwargs['slug'],
        )

    def to_internal_value(self, value):
        format = None
        try:
            format = Format.objects.get(
                slug=value,
            )
        except:
            raise serializers.ValidationError("Media format not found.")

        return format


# Author serializers
class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for author objects"""

    class Meta:
        model = Author
        fields = ('name', 'sex', 'date_of_birth', 'biography')
        read_only_fields = ('id',)
        lookup_field = 'slug'


class AuthorDisplaySerializer(serializers.ModelSerializer):
    """Serializer for author objects"""

    class Meta:
        model = Author
        fields = ('name', )
        read_only_fields = ('id', 'name')
        lookup_field = 'slug'


# Track serializers
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
                  'duration', 'medias')
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
            'slug',
            'name',
            'file_url',
            'duration'
        )
        read_only_fields = ('name', 'file_url')


# Media serializer
class MediaSerializer(serializers.ModelSerializer):
    """Serializer for media objects"""

    genre_list = serializers.SerializerMethodField()
    genres = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )

    tracks = serializers.SerializerMethodField()
    language = LanguageDisplayField(many=False)

    media_format = FormatDisplayField(many=False)

    authors = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Author.objects.all()
    )
    author_list = serializers.SerializerMethodField()

    class Meta:
        model = Media
        fields = ('title', 'price', 'discount_price', 'image', 'slug',
                  'estimated_length_in_seconds', 'rating', 'release_date', 'language', 'media_format',
                  'word_count', 'album_type', 'genres', 'genre_list', 'tracks', 'authors', 'author_list')
        read_only_fields = ('id', 'slug')
        lookup_field = 'slug'

    def get_genre_list(self, obj):
        return GenreDisplaySerializer(obj.genres.all(), many=True).data

    def get_tracks(self, obj):
        return TracksDisplaySerializer(obj.tracks.filter(sample=True), many=True).data

    def get_author_list(self, obj):
        return AuthorDisplaySerializer(obj.authors.all(), many=True).data


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
