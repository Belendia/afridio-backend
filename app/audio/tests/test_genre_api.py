from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Genre
from audio.serializers import GenreSerializer


GENRE_URL = reverse('audio:genre-list')


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
