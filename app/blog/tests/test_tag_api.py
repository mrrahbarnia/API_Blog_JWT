"""
Test tag API's.
"""
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag
from ..api.v1.serializers import TagSerializer


LIST_TAG_URL = reverse('blog:api-blog:tag-list')


def tag_detail_url(tag_id):
    """Create and return tag detail URL."""
    url = reverse('blog:api-blog:tag-detail', args=[tag_id])
    return url


def create_user(email='Test@example.com', password='T123@example'):
    """Create and return a sample user."""
    user = get_user_model().objects.create_user(
        email=email, password=password
        )
    return user


def create_tag(user, name='IT'):
    """Create and return a tag instance."""
    tag = Tag.objects.create(user=user, name=name)
    return tag


class PublicUserTagTests(TestCase):
    """Test unauthenticated requests."""
    def setUp(self):
        self.client = APIClient()

    def test_get_list_of_tags_successfully(self):
        """Test GET list of existing tags
        without authenticated successfully."""
        sample_user = create_user()
        create_tag(user=sample_user)
        create_tag(user=sample_user, name='Sample tag')

        res = self.client.get(LIST_TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), 2)

    def test_retrieve_detail_tag_successfully(self):
        """Test retrieving tag detail with unauthenticated
        without deleting and updating permissions."""
        sample_user = create_user()
        sample_tag = create_tag(user=sample_user)
        url = tag_detail_url(sample_tag.id)

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = TagSerializer(sample_tag)
        self.assertEqual(res.data, serializer.data)

    def test_create_tag_unauthenticated_unsuccessfully(self):
        """Test creating tags with unauthenticated
        request unsuccessfully."""
        payload = {
            'name': 'Sample tag'
        }
        res = self.client.post(LIST_TAG_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserTagTests(TestCase):
    """Test authenticated requests"""
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_delete_or_update_other_user_tags_unsuccessful(self):
        """Test deleting or updating the
        tags of other users unsuccessfully."""
        another_user = get_user_model().objects.create_user(
            email='another@example.com', password='T123@example'
        )
        sample_tag = create_tag(user=another_user)
        url = tag_detail_url(sample_tag.id)

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        payload = {
            'name': 'edited'
        }
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(sample_tag.name, 'IT')

    def test_create_tag_successfully(self):
        """Test creating tags successfully."""
        payload = {
            'name': 'Sample tag'
        }
        res = self.client.post(LIST_TAG_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Tag.objects.filter(name='Sample tag').exists())

    def test_update_tag_successfully(self):
        """Test updating tags successfully."""
        payload = {
            'name': 'Sample tag'
        }
        sample_tag = create_tag(user=self.user)
        url = tag_detail_url(sample_tag.id)

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        sample_tag.refresh_from_db()
        self.assertEqual(sample_tag.name, payload['name'])

    def test_delete_tag_successfully(self):
        """Test deleting tags successfully."""
        sample_tag = create_tag(user=self.user)
        url = tag_detail_url(sample_tag.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(user=self.user).exists())
