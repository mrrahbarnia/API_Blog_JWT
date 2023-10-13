"""
Test post API's.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Profile,
    Post
)


LIST_POST_URL = reverse('blog:api-blog:post-list')


def post_detail_url(post_id):
    """Create and return post detail URL."""
    url = reverse('blog:api-blog:post-detail', args=[post_id])
    return url


def create_user(**params):
    """Create and return users."""
    user = get_user_model().objects.create_user(**params)
    return user


def create_post(author, **params):
    """Create and return posts."""
    defaults = {
        'title': 'Sample title',
        'content': 'Sample content',
        'published_date': "2023-10-12T16:48:32.691Z",
        'status': True
    }
    defaults.update(**params)
    post = Post.objects.create(author=author, **defaults)
    return post


class PublicUserPostTests(TestCase):
    """Test unauthenticated requests."""
    def setUp(self):
        self.client = APIClient()

    def test_retrieve_list_of_posts_successfully(self):
        """Test listing posts successfully."""
        sample_user = create_user(
            email='Test@example.com', password='T123@example'
            )
        create_post(author=Profile.objects.get(user=sample_user))
        create_post(author=Profile.objects.get(user=sample_user))

        res = self.client.get(LIST_POST_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_post_without_authentication(self):
        """Test POST method for creating posts without authentication."""
        res = self.client.post(LIST_POST_URL, {})

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_post_with_unauthenticated_user(self):
        """Test for updating posts in detail url with
        unauthenticated user and get 405 not allowed."""
        payload = {
            'title': 'edited'
        }

        sample_user = create_user(
            email='Test@example.com', password='T123@example'
            )
        profile = Profile.objects.get(user=sample_user)
        post = create_post(author=profile)
        url = post_detail_url(post.id)

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_post_with_unauthenticated_user(self):
        """Test for deleting posts in detail url with
        unauthenticated user and get 405 not allowed."""
        sample_user = create_user(
            email='Test@example.com', password='T123@example'
            )
        profile = Profile.objects.get(user=sample_user)
        post = create_post(author=profile)
        url = post_detail_url(post.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserPostTests(TestCase):
    """Test authenticated requests."""
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='Test@example.com', password='T123@example'
            )
        self.client.force_authenticate(self.user)
        self.profile = Profile.objects.get(user=self.user)

    def test_create_post_successfully(self):
        """Test POST method for creating posts
        whithout author field while authenticated."""
        payload = {
            'title': 'Django',
            'content': 'Django advanced course.',
            'published_date': "2023-10-12T16:48:32.691Z"
        }
        res = self.client.post(LIST_POST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Post.objects.filter(author=self.profile).exists())

    def test_get_post_detail_successfully(self):
        """Test for getting post detail and see content of the post."""
        post = create_post(author=self.profile)
        url = post_detail_url(post.id)

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('content', res.data)

    def test_showing_content_only_on_detail(self):
        """Test showing content field only on detail
        and not showing abs_url and snippet."""
        post = create_post(author=self.profile)
        url = post_detail_url(post.id)

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('content', res.data)
        self.assertNotIn('snippet', res.data)
        self.assertNotIn('abs_url', res.data)

    def test_partial_update_post_successfully(self):
        """Test updating posts in detail url successfulyy."""
        payload = {
            'content': 'content-edited'
        }
        post = create_post(author=self.profile)
        url = post_detail_url(post.id)

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertEqual(post.title, 'Sample title')
        self.assertEqual(post.content, 'content-edited')

    def test_full_update_post_successfully(self):
        """Test full updating posts with PUT method successfully."""
        payload = {
            'title': 'edited-title',
            'content': 'edited_content',
            'published_date': "2023-10-12T16:48:32.691Z"
        }
        post = create_post(author=self.profile)
        url = post_detail_url(post.id)

        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertEqual(post.title, payload['title'])
        self.assertEqual(post.content, payload['content'])

    def test_delete_post_successfully(self):
        """Test deleting posts successfully."""
        post = create_post(author=self.profile)
        url = post_detail_url(post.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(author=self.profile).exists())

    def test_update_another_user_raises_error(self):
        """Test updating the posts belong to another users unsuccessfully."""
        payload = {
            'title': 'edited'
        }
        anonymous = create_user(
            email='anonymous@example.com', password='A123@example'
            )
        anonymous_profile = Profile.objects.get(user=anonymous)
        post = create_post(author=anonymous_profile)
        url = post_detail_url(post.id)

        self.client.patch(url, payload)
        post.refresh_from_db()

        self.assertEqual(post.title, 'Sample title')

    def test_delete_another_user_post_unsuccessfully(self):
        """Test deleting another user posts
        unsuccessfully beacuase of permissions."""
        anonymous = create_user(
            email='anonymous@example.com', password='A123@example'
            )
        anonymous_profile = Profile.objects.get(user=anonymous)
        post = create_post(author=anonymous_profile)
        url = post_detail_url(post.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Post.objects.filter(author=anonymous_profile).exists())