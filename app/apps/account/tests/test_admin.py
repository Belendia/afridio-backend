from datetime import date

from django .test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@habeltech.com',
            password='password123',
            name='admin',
            sex='UNSURE',
            date_of_birth=date.today(),
            phone='+251911000000'
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='test@habeltech.com',
            password='password123',
            name='Test account full name',
            sex='FEMALE',
            date_of_birth=date.today(),
            phone='+251911000000'
        )

    def test_users_listed(self):
        """Test that users are listed on account page"""

        url = reverse('admin:core_user_changelist')
        response = self.client.get(url)

        self.assertContains(response, self.user.name)
        self.assertContains(response, self.user.email)

    def test_user_change_page(self):
        """Test that the account edit page works"""

        # /admin/core/account/1
        url = reverse('admin:core_user_change', args=[self.user.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_create_user_page(self):
        """Test that the create account page works"""

        url = reverse('admin:core_user_add')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
