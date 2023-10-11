"""
Test user API.
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Profile


CREATE_USER_URL = reverse('user:api-user:registration')
TOKEN_LOGIN_URL = reverse('user:api-user:token-login')
TOKEN_LOGOUT_URL = reverse('user:api-user:token-logout')
CHANGE_PASSWORD_URL = reverse('user:api-user:change-password')
JWT_CREATE_URL = reverse('user:api-user:jwt-create')
PROFILE_URL = reverse('user:api-user:profile')
RESEND_ACTIVATION_URL = reverse('user:api-user:resend-activation')
RESET_PASSWORD_URL = reverse('user:api-user:reset-password')


def create_user(**params):
    """Create and return a user."""
    return get_user_model().objects.create_user(**params)


def activation_url(token):
    """Create and return a user activation url."""
    return reverse('user:api-user:activation', args=[token])


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
        create_user(
            email=payload['email'],
            password=payload['password'],
            is_verified=True
        )
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

    def test_retrieve_profile_unauthorized(self):
        """Test for retrieving profile endpoint with unauthenticated user."""
        res = self.client.get(PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_activation_url_post_not_allowed_405(self):
        """Test not allowed posting method for activation URL."""
        url = activation_url({})
        res = self.client.post(url, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_resend_activation_with_not_existing_email(self):
        """Test resend avtivation URL with not existing email."""
        payload = {
            'email': 'Test@example.com'
        }
        res = self.client.post(RESEND_ACTIVATION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_resend_activation_with_existing_email(self):
        """Test resend activation URL with existing email."""
        payload = {
            'email': 'Test@example.com'
        }
        create_user(email=payload['email'], password='T123@example')
        res = self.client.post(RESEND_ACTIVATION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_resend_activation_url_with_verified_user(self):
        """Test resend activation URL with a verified user."""
        payload = {
            'email': 'T123@example.com'
        }
        create_user(email=payload['email'],
                    password='T123@example',
                    is_verified=True)
        res = self.client.post(RESEND_ACTIVATION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_url_with_not_existing_email(self):
        """Test reset password URL with not existing email."""
        payload = {
            'email': 'T123@example.com'
        }
        res = self.client.post(RESET_PASSWORD_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_url_successfully(self):
        """Test reset password URL successfully with response 200."""
        payload = {
            'email': 'T123@example.com'
        }
        create_user(email=payload['email'], password='T123@example')
        res = self.client.post(RESET_PASSWORD_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)


class PrivateUserApiTest(TestCase):
    """Tests API requests that required authentication."""
    def setUp(self):
        self.user = create_user(
            email="Test@example.com", password="T123@example", is_verified=True
            )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

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

    def test_token_generator_for_showing_id_and_email_in_response(self):
        """Test for exhibiting user id and user email in response."""
        payload = {
            "email": "Test@example.com",
            "password": "T123@example",
        }
        res = self.client.post(TOKEN_LOGIN_URL, payload)

        self.assertIn('user_id', res.data)
        self.assertIn('email', res.data)

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

    def test_retrieve_profile_endpoint_authenticated(self):
        """Test retrieving profile endpoint with authenticated user."""
        res = self.client.get(PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_post_method_for_profile_not_allowed(self):
        """Test POST method for profile endpoint
        is not allowed and returns 405."""
        res = self.client.post(PROFILE_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_updating_profile_successfully(self):
        """Test for updating profile's successfully."""
        sample_profile = Profile.objects.get(
            user=self.user
        )
        payload = {
            'first_name': 'Ali-updated'
        }

        res = self.client.patch(PROFILE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        sample_profile.refresh_from_db()
        self.assertEqual(sample_profile.first_name, payload['first_name'])
