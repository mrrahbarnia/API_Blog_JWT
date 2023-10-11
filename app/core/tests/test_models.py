"""
Tests for models.
"""
from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successfully(self):
        """
        Test for creating a user with email instead
        of username using create_user successfully.
        """
        test_user = get_user_model().objects.create_user(
            email="test@example.com",
            password="T123@example"
        )

        self.assertTrue(test_user.is_active)
        self.assertFalse(test_user.is_staff)
        self.assertFalse(test_user.is_verified)
        self.assertFalse(test_user.is_superuser)
        self.assertTrue(
            get_user_model().objects.filter(
                email="test@example.com").exists()
                )
        self.assertEqual(test_user.email, "test@example.com")
        self.assertTrue(test_user.check_password("T123@example"))
        try:
            self.assertIsNone(test_user.username)
        except AttributeError:
            pass

    def test_create_user_with_blank_password(self):
        """Test for required password."""
        get_user_model().objects.create_user(
            email="test1@example.com",
            password=""
        )

        self.assertFalse(
            get_user_model().objects.filter(
                email="test@example.com").exists()
                )

    def test_create_user_with_blank_email_raises_error(self):
        """Test for required email."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email="",
                password="T123@example"
            )

    def test_normalizing_email_works_successfully(self):
        """Test for normalizing email."""
        emails = [
            ("Test2@example.com", "Test2@example.com"),
            ("Test3@EXAMPLE.com", "Test3@example.com"),
            ("Test4@example.COM", "Test4@example.com"),
            ("TEST5@EXAMPLE.COM", "TEST5@example.com"),
        ]

        for email, expected in emails:
            test_user = get_user_model().objects.create_user(
                email, "T123@example"
                )
            self.assertEqual(test_user.email, expected)

    def test_create_super_user_successfully(self):
        """
        Test for creating an admin user
        with create_superuser successfully.
        """
        test_user = get_user_model().objects.create_superuser(
            email="test8@example.com",
            password="T123@example"
        )

        self.assertTrue(test_user.is_staff)
        self.assertTrue(test_user.is_verified)
        self.assertTrue(test_user.is_superuser)
        self.assertTrue(
            get_user_model().objects.filter(
                email="test8@example.com").exists()
                )
        self.assertEqual(test_user.email, "test8@example.com")
        self.assertTrue(test_user.check_password("T123@example"))

    def test_profile_created_after_adding_user_account(self):
        """
        Test for checking whether profile will create
        successfully after creating a user or not.
        """
        test_user = get_user_model().objects.create_user(
            email="test9@example.com",
            password="T123@example"
        )

        self.assertTrue(
            models.Profile.objects.filter(user=test_user).exists()
        )

    @patch('core.models.uuid.uuid4')
    def test_uploading_profile_image_in_correct_path(self, mock_uuid):
        """Test for checking the path of uploading profile images."""
        uuid = 'uuid-test'
        mock_uuid.return_value = uuid
        file_path = models.profile_images_file_path(None, 'example.png')

        self.assertEqual(file_path, f'uploads/profile/{uuid}.png')
