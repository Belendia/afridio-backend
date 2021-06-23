from rest_framework import serializers
import json

from apps.media.models import Genre, Track, Media, Language, Format, Author, Image

from apps.common.utils.validators import validate_image_size, validate_file_type


class SlugRelatedField(serializers.SlugRelatedField):
    """Serializer for author objects"""

    def to_representation(self, value):
        return value.name


class ImageSlugRelatedField(serializers.SlugRelatedField):
    """Serializer for author objects"""

    def to_representation(self, value):
        return {'slug': value.slug, 'width': value.size.width, 'image': value.file.url}


class MediaSlugRelatedField(serializers.SlugRelatedField):
    """Serializer for author objects"""

    def to_representation(self, value):
        return value.title


class AuthorSlugRelatedField(serializers.SlugRelatedField):
    """Serializer for author objects"""

    def to_representation(self, value):
        serializer = ImageSerializer(value.images, many=True)
        return {"name": value.name, "slug": value.slug, "photo": serializer.data}


# Genre Serializers
class GenreSerializer(serializers.ModelSerializer):
    """Serializer for genre objects"""

    class Meta:
        model = Genre
        fields = ('slug', 'name')
        read_only_fields = ('id', 'slug')
        lookup_field = 'slug'


# Language Serializers
class LanguageSerializer(serializers.ModelSerializer):
    """Serializer for language objects"""

    class Meta:
        model = Language
        fields = ('name',)
        read_only_fields = ('id',)
        lookup_field = 'id'


# class LanguageDisplayField(serializers.RelatedField):
#     def to_representation(self, value):
#         return value.name
#
#     def get_queryset(self):
#
#         return Language.objects.filter(
#             slug=self.kwargs['slug'],
#         )
#
#     def to_internal_value(self, value):
#         language = None
#         try:
#             language = Language.objects.get(
#                 slug=value,
#             )
#         except:
#             raise serializers.ValidationError("Language not found.")
#
#         return language


# Media format serializers
class FormatSerializer(serializers.ModelSerializer):
    """Serializer for media format objects"""

    class Meta:
        model = Format
        fields = ('name', 'sequence')
        read_only_fields = ('id',)
        lookup_field = 'slug'


# Author serializers
class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for author objects"""

    class Meta:
        model = Author
        fields = ('name', 'sex', 'date_of_birth', 'biography')
        read_only_fields = ('id',)
        lookup_field = 'slug'


# Image Serializers
class ImageSerializer(serializers.ModelSerializer):
    """Serializer for language objects"""

    class Meta:
        model = Image
        fields = ('slug', 'file')
        read_only_fields = ('id',)
        lookup_field = 'slug'


# Track serializers
class TrackSerializer(serializers.ModelSerializer):
    """Serializer for track objects"""

    medias = MediaSlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Media.objects.all()
    )

    class Meta:
        model = Track
        fields = ('slug', 'name', 'popularity', 'file_url', 'sample', 'sequence',
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
            'duration',
            'sequence'
        )
        read_only_fields = ('name', 'file_url')


# Media serializer
class MediaSerializer(serializers.ModelSerializer):
    """Serializer for media objects"""

    genres = SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )

    tracks = serializers.SerializerMethodField()
    # language = LanguageDisplayField(many=False)
    language = SlugRelatedField(
        many=False,
        slug_field='slug',
        queryset=Language.objects.all()
    )

    media_format = SlugRelatedField(
        many=False,
        slug_field='slug',
        queryset=Format.objects.all()
    )

    authors = AuthorSlugRelatedField(many=True, slug_field='slug', queryset=Author.objects.all())
    images = ImageSlugRelatedField(many=True, slug_field='slug', queryset=Image.objects.all())

    class Meta:
        model = Media
        fields = ('title', 'price', 'discount_price', 'slug', 'description', 'estimated_length_in_seconds',
                  'rating', 'release_date', 'language', 'media_format', 'word_count', 'featured',
                  'album_type', 'genres', 'tracks', 'authors', 'images',)
        read_only_fields = ('id', 'slug')
        lookup_field = 'slug'

    def get_tracks(self, obj):
        # return TracksDisplaySerializer(obj.tracks.filter(sample=True), many=True).data
        return TracksDisplaySerializer(obj.tracks.all().order_by('sequence'), many=True).data
