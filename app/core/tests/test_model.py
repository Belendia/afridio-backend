from datetime import datetime

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='test@habeltech.com', password='testpass'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""

        email = "test@habeltech.com"
        password = "Testpass123"

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for the new user is normalized"""

        email = 'test@HABELTECH.com'
        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        """Test creating a new superuser"""

        user = get_user_model().objects.create_superuser(
            'test@habeltech.com',
            'test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_genre_str(self):
        """Test the genre string representation"""

        genre = models.Genre.objects.create(
            name='Fiction',
            user=sample_user()
        )

        self.assertEqual(str(genre), genre.name)

    def test_track_str(self):
        """Test the track string representation"""

        track = models.Track.objects.create(
            name='First track',
            popularity=10,
            original_url='http://localhost/audio/track1.mp3',
            duration_ms=2500,
            user=sample_user()
        )

        self.assertEqual(str(track), track.name)

    def test_audiobook_str(self):
        """Test the audiobook string representation"""

        audiobook = models.AudioBook.objects.create(
            title="The sample audio book",
            word_count=12500,
            estimated_length_in_seconds=25200,
            price=12.50,
            user=sample_user()
        )

        self.assertEqual(str(audiobook), audiobook.title)

    def test_album_str(self):
        """Test the album string representation"""

        album = models.Album.objects.create(
            name="Sample album",
            album_type=models.Album.AlbumType.ALBUM,
            estimated_length_in_seconds=25200,
            popularity=35,
            price=12.50,
            release_date=datetime.now(),
            user=sample_user()
        )

        self.assertEqual(str(album), album.name)
