from datetime import date

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Genre, Media
from media.serializers import GenreSerializer


GENRE_URL = reverse('media:genres-list', kwargs={"version": "v1"})


class PublicGenreApiTests(TestCase):
    """Test the publicly available genre API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_not_required(self):
        """Test that login is not required for retrieving genre"""

        res = self.client.get(GENRE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class PrivateGenreApiTest(TestCase):
    """Test the authorized user genre API"""

    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            'test@habeltech.com',
            'password123',
            name='admin',
            sex='UNSURE',
            date_of_birth=date.today(),
            phone='+251911000000'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_genres(self):
        """Test retrieving genres"""

        Genre.objects.create(user=self.user, name='Novel')
        Genre.objects.create(user=self.user, name='Fiction')

        res = self.client.get(GENRE_URL)

        genres = Genre.objects.all().order_by('-id')
        serializer = GenreSerializer(genres, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'], serializer.data)

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

    def test_retrieve_genres_assigned_to_medias(self):
        """Test filtering genres by those assigned to medias"""

        genre1 = Genre.objects.create(user=self.user, name='Fiction')
        genre2 = Genre.objects.create(user=self.user, name='Novel')

        media = Media.objects.create(
            title='Sample media book',
            word_count=14543,
            estimated_length_in_seconds=25000,
            price=12.50,
            user=self.user
        )
        media.genres.add(genre1)

        res = self.client.get(GENRE_URL, {'assigned_only': 1})

        serializer1 = GenreSerializer(genre1)
        serializer2 = GenreSerializer(genre2)

        self.assertIn(serializer1.data, res.data['results'])
        self.assertNotIn(serializer2.data, res.data['results'])

    def test_retrieve_genres_assigned_to_medias_unique(self):
        """Test filtering genres by assigned returns unique medias"""

        genre = Genre.objects.create(user=self.user, name='Fiction')
        Genre.objects.create(user=self.user, name='Novel')

        media1 = Media.objects.create(
            title='Sample media book',
            word_count=14543,
            estimated_length_in_seconds=25000,
            price=12.50,
            user=self.user
        )
        media1.genres.add(genre)

        media2 = Media.objects.create(
            title='Audio book 2',
            word_count=25543,
            estimated_length_in_seconds=15000,
            price=10.50,
            user=self.user
        )
        media2.genres.add(genre)

        res = self.client.get(GENRE_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data['results']), 1)
