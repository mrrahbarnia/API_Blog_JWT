"""
Test category API's.
"""
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Category
from ..api.v1.serializers import CategorySerializer


LIST_CATEGORY_URL = reverse('blog:api-blog:category-list')


def category_detail_url(category_id):
    """Create and return category detail URL."""
    url = reverse('blog:api-blog:category-detail', args=[category_id])
    return url


def create_user(email='Test@example.com', password='T123@example'):
    """Create and return a sample user."""
    user = get_user_model().objects.create_user(
        email=email, password=password
        )
    return user


def create_category(user, name='Programming'):
    """Create and return a category instance."""
    category = Category.objects.create(user=user, name=name)
    return category


class PublicUserCategoryTests(TestCase):
    """Test unauthenticated requests."""
    def setUp(self):
        self.client = APIClient()

    def test_get_list_of_categories_successfully(self):
        """Test GET list of existing categories
        without authenticated successfully."""
        sample_user = create_user()
        create_category(user=sample_user)
        create_category(user=sample_user, name='Django')

        res = self.client.get(LIST_CATEGORY_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        categories = Category.objects.all().order_by('-name')
        serializer = CategorySerializer(categories, many=True)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), 2)

    def test_retrieve_detail_category_successfully(self):
        """Test retrieving category detail with unauthenticated
        without deleting and updating permissions."""
        sample_user = create_user()
        category = create_category(user=sample_user)
        url = category_detail_url(category.id)

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = CategorySerializer(category)
        self.assertEqual(res.data, serializer.data)

    def test_create_category_unauthenticated_unsuccessfully(self):
        """Test creating categories with
        unauthenticated request unsuccessfully."""
        payload = {
            'name': 'Python'
        }
        res = self.client.post(LIST_CATEGORY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserCategoryTests(TestCase):
    """Test authenticated requests."""
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_delete_or_update_other_user_categories_unsuccessful(self):
        """Test deleting or updating the
        categories of other users unsuccessfully."""
        another_user = get_user_model().objects.create_user(
            email='another@example.com', password='T123@example'
        )
        category = create_category(user=another_user)
        url = category_detail_url(category.id)

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        payload = {
            'name': 'edited'
        }
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(category.name, 'Programming')

    def test_create_category_successfully(self):
        """Test creating categories successfully."""
        payload = {
            'name': 'Python'
        }
        res = self.client.post(LIST_CATEGORY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(name='Python').exists())

    def test_update_category_successfully(self):
        """Test updating categories successfully."""
        payload = {
            'name': 'edited'
        }
        category = create_category(user=self.user)
        url = category_detail_url(category.id)

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        category.refresh_from_db()
        self.assertEqual(category.name, payload['name'])

    def test_delete_category_successfully(self):
        """Test deleting categories successfully."""
        category = create_category(user=self.user)
        url = category_detail_url(category.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(user=self.user).exists())
