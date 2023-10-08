"""
Test user API.
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:api-user:registration')
TOKEN_LOGIN_URL = reverse('user:api-user:token-login')
TOKEN_LOGOUT_URL = reverse('user:api-user:token-logout')
CHANGE_PASSWORD_URL = reverse('user:api-user:change-password')
JWT_CREATE_URL = reverse('user:api-user:jwt-create')
# JWT_REFRESH_URL = reverse('user:api-user:jwt-refresh')
# JWT_VERIFY_URL = reverse('user:api-user:jwt-verify')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTest(TestCase):
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
            'email': 'Test@example.com',
            'password': 'T123@example',
            'password1': 'T123@example',
        }
        create_user(email="Test@example.com", password="T123@example")
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """
        Test for checking whether the password
        is less than 8 chars or not.
        """
        payload = {
            'email': 'Test@example.com',
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
            'email': 'Test@example.com',
            'password': '123456789',
            'password1': '123456789',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(get_user_model().objects.filter(
            email=payload['email']).exists()
            )

    def test_token_url_generates_token_successfully(self):
        """Test for operation of token generator url."""
        payload = {
            "email": "Test@example.com",
            "password": "T123@example",
        }
        create_user(email=payload['email'], password=payload['password'])
        res = self.client.post(TOKEN_LOGIN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_token_url_generates_token_with_bad_credentials(self):
        """Test token generator url with bad credentials."""
        payload = {
            "email": "Test@example.com",
            "password": "T123@example",
        }
        create_user(email=payload['email'], password="T123@examplee")
        res = self.client.post(TOKEN_LOGIN_URL, payload)

        self.assertEqual(res.status_code, 400)
        self.assertNotIn('token', res.data)

    def test_token_url_generates_with_blank_password(self):
        """Test token generator url with blank password."""
        payload = {
            "email": "Test@example.com",
            "password": "",
        }
        create_user(email=payload['email'], password="T123@examplee")
        res = self.client.post(TOKEN_LOGIN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_jwt_unauthorized(self):
        """Test creating jwt with unauthenticated user."""
        payload = {
            'email': 'Test@example.com',
            'password': 'T123@example'
        }
        res = self.client.post(JWT_CREATE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTest(TestCase):
    """Tests API requests that required authentication."""
    def setUp(self):
        self.user = create_user(
            email="Test@example.com", password="T123@example"
            )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_token_generator_for_showing_id_and_email_in_response(self):
        """Test for exhibiting user id and user email in response."""
        payload = {
            "email": "Test@example.com",
            "password": "T123@example",
        }
        res = self.client.post(TOKEN_LOGIN_URL, payload)

        self.assertIn('user_id', res.data)
        self.assertIn('email', res.data)

    def test_get_change_password_url_not_allowed(self):
        """Test for get change password URL with loggedin users."""
        res = self.client.get(CHANGE_PASSWORD_URL)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_post_change_password_url_not_allowed(self):
        """Test POST is not allowed method for change password endpoint."""
        res = self.client.post(CHANGE_PASSWORD_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_change_password_successfully(self):
        """Test change password successfully."""
        payload = {
            'old_password': 'T123@example',
            'new_password': 'T123@examplee',
            'new_password1': 'T123@examplee'
        }
        res = self.client.put(CHANGE_PASSWORD_URL, payload)
        self.user.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.check_password(payload['new_password']))

    def test_destroy_auth_token_with_response_204(self):
        """Test for destroying auth token successfully."""
        payload = {
            'email': "Test@example.com", 'password': "T123@example"
        }
        res = self.client.post(TOKEN_LOGIN_URL, payload)
        res = self.client.post(TOKEN_LOGOUT_URL, {})

        self.assertEqual(res.status_code, 204)

    def test_create_jwt_with_authenticated_user_successfully(self):
        """Test for creating jwt by POST method successfully."""
        payload = {
            'email': 'Test@example.com',
            'password': 'T123@example'
        }

        res = self.client.post(JWT_CREATE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)
        self.assertIn('email', res.data)
        self.assertIn('id', res.data)
