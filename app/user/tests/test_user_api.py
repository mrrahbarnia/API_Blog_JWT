"""
Test user API.
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:api-user:registration')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class TestUserAPI(TestCase):
    """Tests for user API."""
    def setUp(self):
        self.client = APIClient()

    def test_create_user_api_endpoint_response_201(self):
        """Test create user endpoint works successfully."""
        payload = {
            'email': 'Test@example.com',
            'password': 'T123@example',
            'password1': 'T123@example',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(get_user_model().objects.filter(
            email=payload['email'])
            )
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn(payload['password'], res.data)
        self.assertNotIn(payload['password1'], res.data)

    def test_create_user_with_email_exists_response_400(self):
        """Test for failed endpoint with existing email."""
        payload = {
            'email': 'Test1@example.com',
            'password': 'T123@example',
            'password1': 'T123@example',
        }
        create_user(email="Test1@example.com", password="T123@example")
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """
        Test for checking whether the password
        is less than 8 chars or not.
        """
        payload = {
            'email': 'Test2@example.com',
            'password': 'T@12345',
            'password1': 'T@12345',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(get_user_model().objects.filter(
            email=payload['email']).exists()
            )

    def test_for_complexity_of_password(self):
        """
        Test for checking whether the
        password is complex enough or not.
        """
        payload = {
            'email': 'Test3@example.com',
            'password': '123456789',
            'password1': '123456789',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(get_user_model().objects.filter(
            email=payload['email']).exists()
            )
