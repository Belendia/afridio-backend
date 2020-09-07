from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Genre, AudioBook, Album
from audio.serializers import GenreSerializer


GENRE_URL = reverse('audio:genres-list', kwargs={"version": "v1"})


class PublicGenreApiTests(TestCase):
    """Test the publicly available genre API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving genre"""

        res = self.client.get(GENRE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateGenreApiTest(TestCase):
    """Test the authorized user genre API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@habeltech.com',
            'password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_genres(self):
        """Test retrieving genres"""

        Genre.objects.create(user=self.user, name='Novel')
        Genre.objects.create(user=self.user, name='Fiction')

        res = self.client.get(GENRE_URL)

        genres = Genre.objects.all().order_by('-name')
        serializer = GenreSerializer(genres, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_genre_successful(self):
        """Test creating a new genre"""

        payload = {'name': 'Fiction'}
        self.client.post(GENRE_URL, payload)

        exists = Genre.objects.filter(
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_genre_invalid(self):
        """Test creating a new tag with invalid payload"""

        payload = {'name': ''}
        res = self.client.post(GENRE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_genres_assigned_to_audiobooks(self):
        """Test filtering genres by those assigned to audiobooks"""

        genre1 = Genre.objects.create(user=self.user, name='Fiction')
        genre2 = Genre.objects.create(user=self.user, name='Novel')

        audiobook = AudioBook.objects.create(
            title='Sample audio book',
            word_count=14543,
            estimated_length_in_seconds=25000,
            price=12.50,
            user=self.user
        )
        audiobook.genres.add(genre1)

        res = self.client.get(GENRE_URL, {'audiobook_assigned_only': 1})

        serializer1 = GenreSerializer(genre1)
        serializer2 = GenreSerializer(genre2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_genres_assigned_to_audiobooks_unique(self):
        """Test filtering genres by assigned returns unique audiobooks"""

        genre = Genre.objects.create(user=self.user, name='Fiction')
        Genre.objects.create(user=self.user, name='Novel')

        audiobook1 = AudioBook.objects.create(
            title='Sample audio book',
            word_count=14543,
            estimated_length_in_seconds=25000,
            price=12.50,
            user=self.user
        )
        audiobook1.genres.add(genre)

        audiobook2 = AudioBook.objects.create(
            title='Audio book 2',
            word_count=25543,
            estimated_length_in_seconds=15000,
            price=10.50,
            user=self.user
        )
        audiobook2.genres.add(genre)

        res = self.client.get(GENRE_URL, {'audiobook_assigned_only': 1})

        self.assertEqual(len(res.data), 1)

    def test_retrieve_genres_assigned_to_albums(self):
        """Test filtering genres by those assigned to albums"""

        genre1 = Genre.objects.create(user=self.user, name='Jazz')
        genre2 = Genre.objects.create(user=self.user, name='Rock')

        album = Album.objects.create(
            name='Sample album',
            album_type='ALBUM',
            estimated_length_in_seconds=25525,
            popularity=35,
            price=12.50,
            release_date='2020-09-04',
            user=self.user
        )
        album.genres.add(genre1)

        res = self.client.get(GENRE_URL, {'album_assigned_only': 1})

        serializer1 = GenreSerializer(genre1)
        serializer2 = GenreSerializer(genre2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_genres_assigned_to_albums_unique(self):
        """Test filtering genres by assigned returns unique albums"""

        genre = Genre.objects.create(user=self.user, name='Fiction')
        Genre.objects.create(user=self.user, name='Novel')

        album1 = Album.objects.create(
            name='Sample album',
            album_type='ALBUM',
            estimated_length_in_seconds=25525,
            popularity=35,
            price=12.50,
            release_date='2020-09-04',
            user=self.user
        )
        album1.genres.add(genre)

        album2 = Album.objects.create(
            name='Sample album',
            album_type='ALBUM',
            estimated_length_in_seconds=25525,
            popularity=35,
            price=12.50,
            release_date='2020-09-04',
            user=self.user
        )
        album2.genres.add(genre)

        res = self.client.get(GENRE_URL, {'album_assigned_only': 1})

        self.assertEqual(len(res.data), 1)
