"""
Test comment API.s.
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Profile,
    Comment,
    Post
)
from ..api.v1.serializers import CommentSerializer


LIST_COMMENT_URL = reverse('blog:api-blog:comment-list')


def comment_detail_url(comment_id):
    """Create and return comment detail URL."""
    url = reverse('blog:api-blog:comment-detail', args=[comment_id])
    return url


def create_user(email='Test@example.com', password='T123@example'):
    """Create and return a sample user."""
    user = get_user_model().objects.create_user(
        email=email, password=password
        )
    return user


def create_post(author, **params):
    """Create and return a sample post."""
    defaults = {
        'title': 'Sample title',
        'content': 'Sample content',
        'published_date': "2023-10-12T16:48:32.691Z",
        'status': True
    }
    defaults.update(**params)
    sample_post = Post.objects.create(author=author, **defaults)
    return sample_post


def create_comment(
        post_obj,
        user,
        comment='Sample comment'
        ):
    """Create and return a comment instance."""
    comment = Comment.objects.create(
        post_obj=post_obj, user=user, comment=comment
        )
    return comment


class PublicUserTagTests(TestCase):
    """Test unauthenticated requests."""
    def setUp(self):
        self.client = APIClient()

    def test_get_list_of_comments_successfully(self):
        """Test GET list of existing comments
        unauthenticated successfully."""
        sample_user = create_user()
        sample_profile = Profile.objects.get(user=sample_user)
        sample_post = create_post(author=sample_profile)
        create_comment(post_obj=sample_post, user=sample_user)
        create_comment(post_obj=sample_post, user=sample_user)

        res = self.client.get(LIST_COMMENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        comments = Comment.objects.all().order_by('-comment')
        serializer = CommentSerializer(comments, many=True)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), 2)

    def test_retrieve_detail_comment_unsuccessfully(self):
        """Test retrieving comment detail
        with unauthenticated unsuccessfully."""
        sample_user = create_user()
        sample_profile = Profile.objects.get(user=sample_user)
        sample_post = create_post(author=sample_profile)
        sample_comment = create_comment(post_obj=sample_post, user=sample_user)
        url = comment_detail_url(sample_comment.id)

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_comment_unauthenticated_unsuccessfully(self):
        """Test creating comments with
        unauthenticated requests unsuccessfully."""
        payload = {
            'post_obj': 1,
            'comment': 'Sample comment'
        }
        res = self.client.post(LIST_COMMENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(Comment.objects.filter(
            post_obj=payload['post_obj']).exists())

    def test_update_comment_unauthenticated_unsuccessfully(self):
        """Test updating comments with
        unauthenticated user unsuccessfully."""
        payload = {
            'comment': 'edited'
        }
        sample_user = create_user()
        sample_profile = Profile.objects.get(user=sample_user)
        sample_post = create_post(author=sample_profile)
        sample_comment = create_comment(post_obj=sample_post, user=sample_user)
        url = comment_detail_url(sample_comment.id)

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        sample_comment.refresh_from_db()
        self.assertEqual(sample_comment.comment, 'Sample comment')

    def test_delete_comment_unauthenticated_unsuccessfully(self):
        """Test deleting comments with
        unauthenticated user successfully."""
        sample_user = create_user()
        sample_profile = Profile.objects.get(user=sample_user)
        sample_post = create_post(author=sample_profile)
        sample_comment = create_comment(post_obj=sample_post, user=sample_user)
        url = comment_detail_url(sample_comment.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Comment.objects.filter(user=sample_user).exists())


class PrivateUserCommentTests(TestCase):
    """Test authenticated requests"""
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.profile = Profile.objects.get(user=self.user)

    def test_delete_or_update_other_user_comments_unsuccessful(self):
        """Test deleting or updating the comments of
        other users unsuccessfully while authenticated."""
        another_user = get_user_model().objects.create_user(
            email='another@example.com', password='T123@example'
        )
        sample_post = create_post(author=self.profile)
        sample_comment = create_comment(
            post_obj=sample_post, user=another_user
            )
        url = comment_detail_url(sample_comment.id)

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        payload = {
            'comment': 'edited'
        }
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(sample_comment.comment, 'Sample comment')

    def test_create_comment_successfully(self):
        """Test creating comments with authenticated successfully."""
        sample_post = create_post(author=self.profile)
        payload = {
            'post_obj': 1,
            'comment': 'Sample comment'
        }
        res = self.client.post(LIST_COMMENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(sample_post.author, self.profile)
        self.assertTrue(Comment.objects.filter(
            post_obj=1, comment='Sample comment'
            ).exists())

    def test_update_comment_authenticated_user_successfully(self):
        """Test updating comments only
        for authenticated successfully."""
        payload = {
            'comment': 'edited comment'
        }
        sample_post = create_post(author=self.profile)
        sample_comment = create_comment(post_obj=sample_post, user=self.user)
        url = comment_detail_url(sample_comment.id)

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        sample_comment.refresh_from_db()
        self.assertEqual(sample_comment.comment, payload['comment'])

    def test_delete_comment_successfully(self):
        """Test deleting comments successfully."""
        sample_post = create_post(author=self.profile)
        sample_comment = create_comment(post_obj=sample_post, user=self.user)
        url = comment_detail_url(sample_comment.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(user=self.user).exists())
