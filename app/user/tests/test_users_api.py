from datetime import date

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create', kwargs={"version": "v1"})
TOKEN_URL = reverse('user:token', kwargs={"version": "v1"})
ME_URL = reverse('user:me', kwargs={"version": "v1"})


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""

        payload = {
            'email': 'test@habeltech.com',
            'password': 'Test1234',
            'confirm_password': 'Test1234',
            'name': 'User Name',
            'sex': 'FEMALE',
            'date_of_birth': date.today(),
            'phone': '+251911000000'
        }

        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=response.data['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', response.data)
        self.assertNotIn('confirm_password', response.data)

    def test_user_exists(self):
        """Test creating a user that already exists fails"""
        payload = {
            'email': 'test@habeltech.com',
            'password': 'test1234',
            'name': 'Test',
            'sex': 'FEMALE',
            'date_of_birth': date.today(),
            'phone': '+251911000000'
        }
        create_user(**payload)

        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 5 characters"""

        payload = {
            'email': 'test@habeltech.com',
            'password': 'pw',
            'name': 'Test',
            'sex': 'FEMALE',
            'date_of_birth': date.today(),
            'phone': '+251911000000'
        }
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()

        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""

        payload = {
            'email': 'test@habeltech.com',
            'password': 'test1234',
            'name': 'Test',
            'sex': 'FEMALE',
            'date_of_birth': date.today(),
            'phone': '+251911000000'
        }
        create_user(**payload)

        response = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""

        create_user(
            email='test@habeltech.com',
            password='testpass',
            name='Test user full name',
            sex='FEMALE',
            date_of_birth=date.today(),
            phone='+251911000000'
        )
        payload = {'email': 'test@habeltech.com', 'password': 'wrongpass'}

        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if user doesn't exist"""

        payload = {'email': 'test@habeltech.com', 'password': 'testpass'}
        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are required"""

        response = self.client.post(TOKEN_URL, {'email': '', 'password': ''})

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrive_user_unauthorized(self):
        """Test that authentication is required for users"""

        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.user = create_user(
            email='test@haveltech.com',
            password='testpass',
            name='Name',
            sex='FEMALE',
            date_of_birth='2000-01-01',
            phone='+251911000000'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""

        response = self.client.get(ME_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['name'], self.user.name)
        self.assertEqual(response.data['sex'], self.user.sex)
        self.assertEqual(response.data['phone'], self.user.phone)
        self.assertEqual(response.data['date_of_birth'],
                         self.user.date_of_birth)

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the me URL"""

        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""

        payload = {'name': 'New name', 'password': 'newpassword123'}

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
