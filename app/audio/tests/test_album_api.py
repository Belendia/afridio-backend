from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Album, Genre, Track
from audio.serializers import AlbumSerializer, AlbumDetailSerializer

ALBUMS_URL = reverse('audio:albums-list')


def album_detail_url(audiobook_id):
    """Return album detail URL"""

    return reverse('audio:albums-detail', args=[audiobook_id])


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


def sample_album(user, **params):
    """Create and return a sample album"""

    defaults = {
        'name': 'Sample album',
        'album_type': 'ALBUM',
        'estimated_length_in_seconds': 25525,
        'popularity': 35,
        'price': 12.50,
        'release_date': '2020-09-04'
    }

    defaults.update(params)

    return Album.objects.create(user=user, **defaults)


class PublicAlbumsApiTests(TestCase):
    """Test the publicly available album API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the endpoint"""

        res = self.client.get(ALBUMS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAlbumsApiTest(TestCase):
    """Test the private albums API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@habeltech.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_albums(self):
        """Test retrieving a list of albums"""

        sample_album(self.user, name='Album 2')
        sample_album(self.user, name='Album 1')

        res = self.client.get(ALBUMS_URL)

        albums = Album.objects.all().order_by('-name')
        serializer = AlbumSerializer(albums, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_album_successful(self):
        """Test create a new album"""

        payload = {
            'name': 'Sample album',
            'album_type': 'ALBUM',
            'estimated_length_in_seconds': 25525,
            'popularity': 35,
            'price': 12.50,
            'release_date': '2020-09-04'
        }
        self.client.post(ALBUMS_URL, payload)

        exists = Album.objects.filter(
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_album_invalid(self):
        """Test creating invalid album fails"""

        payload = {
            'name': ''
        }
        res = self.client.post(ALBUMS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_view_album_detail(self):
        """Test viewing a album detail"""

        album = sample_album(user=self.user)
        album.genres.add(sample_genre(user=self.user))
        album.tracks.add(sample_track(user=self.user))

        url = album_detail_url(album.id)
        res = self.client.get(url)

        serializer = AlbumDetailSerializer(album)
        self.assertEqual(res.data, serializer.data)
