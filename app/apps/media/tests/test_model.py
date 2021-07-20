from datetime import datetime, date
# from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from app.media import models


def sample_user(email='test@habeltech.com', password='testpass'):
    """Create a sample account"""
    return get_user_model().objects.create_user(
        email,
        password,
        name='Test account full name',
        sex='FEMALE',
        date_of_birth=datetime.now(),
        phone='+251911000000'
    )


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new account with an email is successful"""

        email = "test@habeltech.com"
        password = "Testpass123"

        user = get_user_model().objects.create_user(
            email=email,
            password=password,
            name='Test account full name',
            sex='FEMALE',
            date_of_birth=datetime.now(),
            phone='+251911000000'
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for the new account is normalized"""

        email = 'test@HABELTECH.com'
        user = get_user_model().objects.create_user(
            email,
            'test123',
            name='Test account full name',
            sex='FEMALE',
            date_of_birth=datetime.now(),
            phone='+251911000000'
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating account with no email raises error"""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                None,
                'test123',
                name='Test account full name',
                sex='FEMALE',
                date_of_birth=datetime.now(),
                phone='+251911000000'
            )

    def test_create_new_superuser(self):
        """Test creating a new superuser"""

        user = get_user_model().objects.create_superuser(
            'test@habeltech.com',
            'test123',
            name='admin',
            sex='UNSURE',
            date_of_birth=date.today(),
            phone='+251911000000'
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

    def test_media_str(self):
        """Test the media string representation"""

        media = models.Media.objects.create(
            title="The sample media book",
            word_count=12500,
            estimated_length_in_seconds=25200,
            price=12.50,
            user=sample_user()
        )

        self.assertEqual(str(media), media.title)

    # @patch('secrets.token_urlsafe')
    # def test_media_file_name_uuid(self, mock_uuid):
    #     """Test that image is saved in the correct location"""
    #
    #     uuid = 'test-uuid'
    #     mock_uuid.return_value = uuid
    #
    #     file_path = models.media_image_file_path(None, 'myimage.jpg')
    #
    #     expected_path = f'uploads/media/{uuid}.jpg'
    #     self.assertEqual(file_path, expected_path)
