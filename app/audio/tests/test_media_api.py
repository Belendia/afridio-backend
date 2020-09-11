import os
import tempfile
from PIL import Image

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Media, Genre, Track
from audio.serializers import MediaSerializer, MediaDetailSerializer

MEDIA_URL = reverse('audio:medias-list', kwargs={"version": "v1"})


def image_upload_url(media_slug):
    """Return URL for media image upload"""
    return reverse('audio:medias-image',
                   kwargs={'slug': media_slug, 'version': 'v1'})


def media_detail_url(media_slug):
    """Return media detail URL"""

    return reverse('audio:medias-detail',
                   kwargs={'slug': media_slug, 'version': 'v1'})


def sample_genre(user, name='Fiction'):
    """Create and return a sample genre"""

    return Genre.objects.create(user=user, name=name)


def sample_track(user, **params):
    """Create and return a sample track"""

    defaults = {
        'name': 'Track 01',
        'popularity': 10,
        'duration_ms': 2500
    }

    defaults.update(params)

    return Track.objects.create(user=user, **defaults)


def sample_media(user, **params):
    """Create and return a sample media"""

    defaults = {
        'title': 'Sample audio book',
        'word_count': 14543,
        'estimated_length_in_seconds': 25000,
        'price': 12.50
    }

    defaults.update(params)

    return Media.objects.create(user=user, **defaults)


class PublicMediaApiTests(TestCase):
    """Test the publicly available medias API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_not_required(self):
        """Test that login is not required to access the endpoint"""

        res = self.client.get(MEDIA_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)


class PrivateMediaApiTest(TestCase):
    """Test the private media API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            'test@habeltech.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_medias(self):
        """Test retrieving a list of audiobooks"""

        sample_media(self.user, title='Audiobook 2')
        sample_media(self.user, title='Audiobook 1')

        res = self.client.get(MEDIA_URL)

        medias = Media.objects.all().order_by('-id')
        serializer = MediaSerializer(medias, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'], serializer.data)

    def test_create_media(self):
        """Test create a new media"""

        payload = {
            'title': 'Sample audio book',
            'word_count': 14543,
            'estimated_length_in_seconds': 25000,
            'price': 12.50,
            'media_format': 'AUDIOBOOK'
        }

        res = self.client.post(MEDIA_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        media = Media.objects.get(slug=res.data['slug'])

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(media, key))

    def test_create_media_with_genres(self):
        """Test creating medias with genre"""

        genre1 = sample_genre(user=self.user, name='Fiction')
        genre2 = sample_genre(user=self.user, name='Fantasy')

        payload = {
            'title': 'The new audiobook',
            'word_count': 16512,
            'estimated_length_in_seconds': 30000,
            'price': 20.50,
            'media_format': 'AUDIOBOOK',
            'genres': [genre1.slug, genre2.slug]
        }

        res = self.client.post(MEDIA_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        media = Media.objects.get(slug=res.data['slug'])
        genres = media.genres.all()

        self.assertEqual(genres.count(), 2)
        self.assertIn(genre1, genres)
        self.assertIn(genre2, genres)

    def test_create_media_with_tracks(self):
        """Test creating medias with tracks"""

        track1 = sample_track(user=self.user, name='Track 01')
        track2 = sample_track(user=self.user, name='Track 02')

        payload = {
            'title': 'The new audiobook',
            'word_count': 16512,
            'estimated_length_in_seconds': 30000,
            'price': 20.50,
            'media_format': 'AUDIOBOOK',
            'tracks': [track1.slug, track2.slug]
        }

        res = self.client.post(MEDIA_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        media = Media.objects.get(slug=res.data['slug'])
        tracks = media.tracks.all()

        self.assertEqual(tracks.count(), 2)
        self.assertIn(track1, tracks)
        self.assertIn(track2, tracks)

    def test_create_media_invalid(self):
        """Test creating invalid media fails"""

        payload = {
            'title': ''
        }
        res = self.client.post(MEDIA_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_view_media_detail(self):
        """Test viewing a media detail"""

        media = sample_media(user=self.user)
        media.genres.add(sample_genre(user=self.user))
        media.tracks.add(sample_track(user=self.user))

        url = media_detail_url(media.slug)

        res = self.client.get(url)

        serializer = MediaDetailSerializer(media)
        self.assertEqual(res.data, serializer.data)

    def test_partial_update_media(self):
        """Test updating an media with patch"""

        media = sample_media(user=self.user)
        media.genres.add(sample_genre(user=self.user))
        new_genre = sample_genre(user=self.user, name='Novel')

        payload = {
            'title': 'Why We Sleep',
            'genres': [new_genre.slug]
        }

        url = media_detail_url(media.slug)
        self.client.patch(url, payload)

        media.refresh_from_db()

        self.assertEqual(media.title, payload['title'])
        genres = media.genres.all()

        self.assertEqual(len(genres), 1)
        self.assertIn(new_genre, genres)

    def test_full_update_media(self):
        """Test updating an media with put"""

        media = sample_media(user=self.user)
        media.genres.add(sample_genre(user=self.user))

        payload = {
            'title': 'Why We Sleep',
            'word_count': 16512,
            'estimated_length_in_seconds': 3029,
            'price': 20.50,
            'media_format': 'AUDIOBOOK',
        }

        url = media_detail_url(media.slug)
        self.client.put(url, payload)

        media.refresh_from_db()
        self.assertEqual(media.title, payload['title'])
        self.assertEqual(media.word_count, payload['word_count'])
        self.assertEqual(media.price, payload['price'])
        genres = media.genres.all()
        self.assertEqual(len(genres), 0)


class MediaImageUploadTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            'test@habeltech.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)
        self.media = sample_media(user=self.user)

    def tearDown(self):
        """Remove all the test files we create to clean up our system"""

        self.media.image.delete()

    def test_upload_image_to_media(self):
        """Test uploading an image to media"""

        url = image_upload_url(self.media.slug)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))  # creates black square image
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.media.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.media.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""

        url = image_upload_url(self.media.slug)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_media_by_genres(self):
        """Test returning media with specific genres"""

        media1 = sample_media(user=self.user, title='Book 1')
        media2 = sample_media(user=self.user, title='Book 2')

        genre1 = sample_genre(user=self.user, name='Fiction')
        genre2 = sample_genre(user=self.user, name='Novel')

        media1.genres.add(genre1)
        media2.genres.add(genre2)

        media3 = sample_media(user=self.user, title='Book 3')

        res = self.client.get(
            MEDIA_URL,
            {'genres': f'{genre1.slug},{genre2.slug}'}
        )

        serializer1 = MediaSerializer(media1)
        serializer2 = MediaSerializer(media2)
        serializer3 = MediaSerializer(media3)

        self.assertIn(serializer1.data, res.data['results'])
        self.assertIn(serializer2.data, res.data['results'])
        self.assertNotIn(serializer3.data, res.data['results'])

    def test_filter_media_by_tracks(self):
        """Test returning media with specific tracks"""

        media1 = sample_media(user=self.user, title='Book 1')
        media2 = sample_media(user=self.user, title='Book 2')

        track1 = sample_track(user=self.user, name='Track 01')
        track2 = sample_track(user=self.user, name='Track 02')

        media1.tracks.add(track1)
        media2.tracks.add(track2)

        media3 = sample_media(user=self.user, title='Book 3')

        res = self.client.get(
            MEDIA_URL,
            {'tracks': f'{track1.slug},{track2.slug}'}
        )

        serializer1 = MediaSerializer(media1)
        serializer2 = MediaSerializer(media2)
        serializer3 = MediaSerializer(media3)

        self.assertIn(serializer1.data, res.data['results'])
        self.assertIn(serializer2.data, res.data['results'])
        self.assertNotIn(serializer3.data, res.data['results'])

    def test_search_media_by_title(self):
        """Test returning media with specific title"""

        media1 = sample_media(user=self.user, title='The Fox')
        media2 = sample_media(user=self.user, title='Strong lions')

        res = self.client.get(
            MEDIA_URL,
            {'search': 'Fox'}
        )

        serializer1 = MediaSerializer(media1)
        serializer2 = MediaSerializer(media2)

        self.assertIn(serializer1.data, res.data['results'])
        self.assertNotIn(serializer2.data, res.data['results'])
