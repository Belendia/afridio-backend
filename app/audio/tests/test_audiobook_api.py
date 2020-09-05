from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import AudioBook, Genre, Track
from audio.serializers import AudioBookSerializer, AudioBookDetailSerializer

AUDIOBOOK_URL = reverse('audio:audiobooks-list')


def audiobook_detail_url(audiobook_id):
    """Return audiobook detail URL"""

    return reverse('audio:audiobooks-detail', args=[audiobook_id])


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

        audiobooks = AudioBook.objects.all().order_by('-title')
        serializer = AudioBookSerializer(audiobooks, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

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

        audiobook = AudioBook.objects.get(id=res.data['id'])

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
            'genres': [genre1.id, genre2.id]
        }

        res = self.client.post(AUDIOBOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        audiobook = AudioBook.objects.get(id=res.data['id'])
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
            'tracks': [track1.id, track2.id]
        }

        res = self.client.post(AUDIOBOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        audiobook = AudioBook.objects.get(id=res.data['id'])
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

        url = audiobook_detail_url(audiobook.id)

        res = self.client.get(url)

        serializer = AudioBookDetailSerializer(audiobook)
        self.assertEqual(res.data, serializer.data)
