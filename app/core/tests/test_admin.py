"""
Test Admin site.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.test import Client


class AdminTest(TestCase):
    """Test Admin page."""

    def setUp(self):
        """Create users and client"""
        self.super_user = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="T1example23@"
        )
        self.client = Client()
        self.client.force_login(self.super_user)
        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="T1example23@"
        )

    def test_showing_list_of_users(self):
        """Test for listing users which have been created."""
        url = reverse("admin:core_user_changelist")
        res = self.client.get(url)

        self.assertContains(res, self.user.email)

    def test_showing_edit_user_page_successfully(self):
        """Test the edit user page works."""
        url = reverse("admin:core_user_change", args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertContains(res, self.user.email)

    def test_create_user_page_works_successfully(self):
        """Test the add user page works."""
        url = reverse("admin:core_user_add")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
