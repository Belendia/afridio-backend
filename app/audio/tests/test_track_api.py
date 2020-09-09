from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Track
from audio.serializers import TrackSerializer

TRACKS_URL = reverse('audio:tracks-list', kwargs={"version": "v1"})


class PublicTrackApiTests(TestCase):
    """Test the publicly available track API"""

    def setUp(self):
        self.client = APIClient()

    def test_login__required(self):
        """Test that login is required to access the endpoint"""

        res = self.client.get(TRACKS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTracksApiTest(TestCase):
    """Test the private track API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@habeltech.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_track_list(self):
        """Test retrieving a list of tracks"""

        Track.objects.create(user=self.user,
                             name='Track 02',
                             popularity=50,
                             duration_ms=2100)
        Track.objects.create(user=self.user,
                             name='Track 01',
                             popularity=10,
                             duration_ms=2500)

        res = self.client.get(TRACKS_URL)

        tracks = Track.objects.all().order_by('-id')
        serializer = TrackSerializer(tracks, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'], serializer.data)

    def test_create_track_successful(self):
        """Test create a new track"""

        payload = {
            'name': 'Track 01',
            'popularity': 10,
            'duration_ms': 2500
        }
        self.client.post(TRACKS_URL, payload)

        exists = Track.objects.filter(
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_track_invalid(self):
        """Test creating invalid track fails"""

        payload = {
            'name': ''
        }
        res = self.client.post(TRACKS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
