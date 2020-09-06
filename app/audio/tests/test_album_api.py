import os
import tempfile
from PIL import Image

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Album, Genre, Track
from audio.serializers import AlbumSerializer, AlbumDetailSerializer

ALBUMS_URL = reverse('audio:albums-list')


def image_upload_url(album_id):
    """Return URL for album image upload"""
    return reverse('audio:albums-image', args=[album_id])


def album_detail_url(album_id):
    """Return album detail URL"""

    return reverse('audio:albums-detail', args=[album_id])


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

    def test_create_album_with_genres(self):
        """Test creating album with genre"""

        genre1 = sample_genre(user=self.user, name='Rock')
        genre2 = sample_genre(user=self.user, name='Funk')

        payload = {
            'name': 'Sample album',
            'album_type': 'ALBUM',
            'estimated_length_in_seconds': 25525,
            'popularity': 35,
            'price': 12.50,
            'release_date': '2020-09-04',
            'genres': [genre1.id, genre2.id]
        }

        res = self.client.post(ALBUMS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        album = Album.objects.get(id=res.data['id'])
        genres = album.genres.all()

        self.assertEqual(genres.count(), 2)
        self.assertIn(genre1, genres)
        self.assertIn(genre2, genres)

    def test_create_album_with_tracks(self):
        """Test creating albums with tracks"""

        track1 = sample_track(user=self.user, name='Track 01')
        track2 = sample_track(user=self.user, name='Track 02')

        payload = {
            'name': 'Sample album',
            'album_type': 'ALBUM',
            'estimated_length_in_seconds': 25525,
            'popularity': 35,
            'price': 12.50,
            'release_date': '2020-09-04',
            'tracks': [track1.id, track2.id]
        }

        res = self.client.post(ALBUMS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        album = Album.objects.get(id=res.data['id'])
        tracks = album.tracks.all()

        self.assertEqual(tracks.count(), 2)
        self.assertIn(track1, tracks)
        self.assertIn(track2, tracks)

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


class AlbumImageUploadTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@habeltech.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)
        self.album = sample_album(user=self.user)

    def tearDown(self):
        """Remove all the test files we create to clean up our system"""

        self.album.image.delete()

    def test_upload_image_to_album(self):
        """Test uploading an image to album"""

        url = image_upload_url(self.album.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))  # creates black square image
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.album.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.album.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""

        url = image_upload_url(self.album.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_album_by_genres(self):
        """Test returning albums with specific genres"""

        album1 = sample_album(user=self.user, name='Music 1')
        album2 = sample_album(user=self.user, name='Music 2')

        genre1 = sample_genre(user=self.user, name='Rock')
        genre2 = sample_genre(user=self.user, name='Jazz')

        album1.genres.add(genre1)
        album2.genres.add(genre2)

        album3 = sample_album(user=self.user, name='Music 3')

        res = self.client.get(
            ALBUMS_URL,
            {'genres': f'{genre1.id}, {genre2.id}'}
        )

        serializer1 = AlbumSerializer(album1)
        serializer2 = AlbumSerializer(album2)
        serializer3 = AlbumSerializer(album3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_album_by_tracks(self):
        """Test returning albums with specific tracks"""

        album1 = sample_album(user=self.user, name='Music 1')
        album2 = sample_album(user=self.user, name='Music 2')

        track1 = sample_track(user=self.user, name='Track 01')
        track2 = sample_track(user=self.user, name='Track 02')

        album1.tracks.add(track1)
        album2.tracks.add(track2)

        album3 = sample_album(user=self.user, name='Music 3')

        res = self.client.get(
            ALBUMS_URL,
            {'tracks': f'{track1.id}, {track2.id}'}
        )

        serializer1 = AlbumSerializer(album1)
        serializer2 = AlbumSerializer(album2)
        serializer3 = AlbumSerializer(album3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
