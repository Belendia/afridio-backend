import os
import tempfile
from PIL import Image

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import AudioBook, Genre, Track
from audio.serializers import AudioBookSerializer, AudioBookDetailSerializer

AUDIOBOOK_URL = reverse('audio:audiobooks-list', kwargs={"version": "v1"})


def image_upload_url(audiobook_slug):
    """Return URL for audiobook image upload"""
    return reverse('audio:audiobooks-image',
                   kwargs={'slug': audiobook_slug, 'version': 'v1'})


def audiobook_detail_url(audiobook_slug):
    """Return audiobook detail URL"""

    return reverse('audio:audiobooks-detail',
                   kwargs={'slug': audiobook_slug, 'version': 'v1'})


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


def sample_audiobook(user, **params):
    """Create and return a sample audiobook"""

    defaults = {
        'title': 'Sample audio book',
        'word_count': 14543,
        'estimated_length_in_seconds': 25000,
        'price': 12.50
    }

    defaults.update(params)

    return AudioBook.objects.create(user=user, **defaults)


class PublicAudioBookApiTests(TestCase):
    """Test the publicly available audiobooks API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the endpoint"""

        res = self.client.get(AUDIOBOOK_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAudioBooksApiTest(TestCase):
    """Test the private audiobook API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@habeltech.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_audiobooks(self):
        """Test retrieving a list of audiobooks"""

        sample_audiobook(self.user, title='Audiobook 2')
        sample_audiobook(self.user, title='Audiobook 1')

        res = self.client.get(AUDIOBOOK_URL)

        audiobooks = AudioBook.objects.all().order_by('-id')
        serializer = AudioBookSerializer(audiobooks, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'], serializer.data)

    def test_create_audiobook(self):
        """Test create a new audiobook"""

        payload = {
            'title': 'Sample audio book',
            'word_count': 14543,
            'estimated_length_in_seconds': 25000,
            'price': 12.50
        }

        res = self.client.post(AUDIOBOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        audiobook = AudioBook.objects.get(slug=res.data['slug'])

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(audiobook, key))

    def test_create_audiobook_with_genres(self):
        """Test creating audiobooks with genre"""

        genre1 = sample_genre(user=self.user, name='Fiction')
        genre2 = sample_genre(user=self.user, name='Fantasy')

        payload = {
            'title': 'The new audiobook',
            'word_count': 16512,
            'estimated_length_in_seconds': 30000,
            'price': 20.50,
            'genres': [genre1.slug, genre2.slug]
        }

        res = self.client.post(AUDIOBOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        audiobook = AudioBook.objects.get(slug=res.data['slug'])
        genres = audiobook.genres.all()

        self.assertEqual(genres.count(), 2)
        self.assertIn(genre1, genres)
        self.assertIn(genre2, genres)

    def test_create_audiobook_with_tracks(self):
        """Test creating audiobooks with tracks"""

        track1 = sample_track(user=self.user, name='Track 01')
        track2 = sample_track(user=self.user, name='Track 02')

        payload = {
            'title': 'The new audiobook',
            'word_count': 16512,
            'estimated_length_in_seconds': 30000,
            'price': 20.50,
            'tracks': [track1.slug, track2.slug]
        }

        res = self.client.post(AUDIOBOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        audiobook = AudioBook.objects.get(slug=res.data['slug'])
        tracks = audiobook.tracks.all()

        self.assertEqual(tracks.count(), 2)
        self.assertIn(track1, tracks)
        self.assertIn(track2, tracks)

    def test_create_audiobook_invalid(self):
        """Test creating invalid audiobook fails"""

        payload = {
            'title': ''
        }
        res = self.client.post(AUDIOBOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_view_audiobook_detail(self):
        """Test viewing a audiobook detail"""

        audiobook = sample_audiobook(user=self.user)
        audiobook.genres.add(sample_genre(user=self.user))
        audiobook.tracks.add(sample_track(user=self.user))

        url = audiobook_detail_url(audiobook.slug)

        res = self.client.get(url)

        serializer = AudioBookDetailSerializer(audiobook)
        self.assertEqual(res.data, serializer.data)

    def test_partial_update_audiobook(self):
        """Test updating an audiobook with patch"""

        audiobook = sample_audiobook(user=self.user)
        audiobook.genres.add(sample_genre(user=self.user))
        new_genre = sample_genre(user=self.user, name='Novel')

        payload = {
            'title': 'Why We Sleep',
            'genres': [new_genre.slug]
        }

        url = audiobook_detail_url(audiobook.slug)
        self.client.patch(url, payload)

        audiobook.refresh_from_db()

        self.assertEqual(audiobook.title, payload['title'])
        genres = audiobook.genres.all()

        self.assertEqual(len(genres), 1)
        self.assertIn(new_genre, genres)

    def test_full_update_audiobook(self):
        """Test updating an audiobook with put"""

        audiobook = sample_audiobook(user=self.user)
        audiobook.genres.add(sample_genre(user=self.user))

        payload = {
            'title': 'Why We Sleep',
            'word_count': 16512,
            'estimated_length_in_seconds': 3029,
            'price': 20.50,
        }

        url = audiobook_detail_url(audiobook.slug)
        self.client.put(url, payload)

        audiobook.refresh_from_db()
        self.assertEqual(audiobook.title, payload['title'])
        self.assertEqual(audiobook.word_count, payload['word_count'])
        self.assertEqual(audiobook.price, payload['price'])
        genres = audiobook.genres.all()
        self.assertEqual(len(genres), 0)


class AudioBookImageUploadTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@habeltech.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)
        self.audiobook = sample_audiobook(user=self.user)

    def tearDown(self):
        """Remove all the test files we create to clean up our system"""

        self.audiobook.image.delete()

    def test_upload_image_to_audiobook(self):
        """Test uploading an image to audiobook"""

        url = image_upload_url(self.audiobook.slug)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))  # creates black square image
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.audiobook.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.audiobook.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""

        url = image_upload_url(self.audiobook.slug)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_audiobook_by_genres(self):
        """Test returning audiobooks with specific genres"""

        audiobook1 = sample_audiobook(user=self.user, title='Book 1')
        audiobook2 = sample_audiobook(user=self.user, title='Book 2')

        genre1 = sample_genre(user=self.user, name='Fiction')
        genre2 = sample_genre(user=self.user, name='Novel')

        audiobook1.genres.add(genre1)
        audiobook2.genres.add(genre2)

        audiobook3 = sample_audiobook(user=self.user, title='Book 3')

        res = self.client.get(
            AUDIOBOOK_URL,
            {'genres': f'{genre1.slug},{genre2.slug}'}
        )

        serializer1 = AudioBookSerializer(audiobook1)
        serializer2 = AudioBookSerializer(audiobook2)
        serializer3 = AudioBookSerializer(audiobook3)

        self.assertIn(serializer1.data, res.data['results'])
        self.assertIn(serializer2.data, res.data['results'])
        self.assertNotIn(serializer3.data, res.data['results'])

    def test_filter_audiobook_by_tracks(self):
        """Test returning audiobooks with specific tracks"""

        audiobook1 = sample_audiobook(user=self.user, title='Book 1')
        audiobook2 = sample_audiobook(user=self.user, title='Book 2')

        track1 = sample_track(user=self.user, name='Track 01')
        track2 = sample_track(user=self.user, name='Track 02')

        audiobook1.tracks.add(track1)
        audiobook2.tracks.add(track2)

        audiobook3 = sample_audiobook(user=self.user, title='Book 3')

        res = self.client.get(
            AUDIOBOOK_URL,
            {'tracks': f'{track1.slug},{track2.slug}'}
        )

        serializer1 = AudioBookSerializer(audiobook1)
        serializer2 = AudioBookSerializer(audiobook2)
        serializer3 = AudioBookSerializer(audiobook3)

        self.assertIn(serializer1.data, res.data['results'])
        self.assertIn(serializer2.data, res.data['results'])
        self.assertNotIn(serializer3.data, res.data['results'])
