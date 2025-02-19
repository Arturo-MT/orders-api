from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from orders.models import Store

User = get_user_model()

class JWTAuthenticationTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.store = Store.objects.create(name="Tienda Test")
        cls.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User",
            store=cls.store
        )
        cls.token_url = reverse('token_obtain_pair')
        cls.token_refresh_url = reverse('token_refresh')

    def setUp(self):
        self.client = APIClient()
        data = {"email": "testuser@example.com", "password": "testpassword"}
        response = self.client.post(self.token_url, data, format="json")
        self.access_token = response.data.get("access")
        self.refresh_token = response.data.get("refresh")

    def test_obtain_token_success(self):
        data = {"email": "testuser@example.com", "password": "testpassword"}
        response = self.client.post(self.token_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_refresh_token_success(self):
        data = {"refresh": self.refresh_token}
        response = self.client.post(self.token_refresh_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_refresh_token_invalid(self):
        data = {"refresh": "invalid_refresh_token"}
        response = self.client.post(self.token_refresh_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access", response.data)