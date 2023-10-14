"""
Test post API's.
"""
import os
import tempfile
from PIL import Image

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Profile,
    Post,
    Category,
    Tag
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


def image_upload_url(post_id):
    """Create and return image url by post's id."""
    return reverse('blog:api-blog:post-upload-image', args=[post_id])


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
            'categories': [],
            'tags': [],
            'published_date': "2023-10-12T16:48:32.691Z"
        }
        res = self.client.post(LIST_POST_URL, payload, format='json')

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
            'categories': [],
            'tags': [],
            'published_date': "2023-10-12T16:48:32.691Z"
        }
        post = create_post(author=self.profile)
        url = post_detail_url(post.id)

        res = self.client.put(url, payload, format='json')

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

    def test_create_post_with_creating_new_categories(self):
        """Test creating posts with new categories."""
        payload = {
            'title': 'Sample title',
            'content': 'Sample content',
            'published_date': "2023-10-12T16:48:32.691Z",
            'categories': [
                {'name': 'Development'}, {'name': 'Sample category'}
                ],
            'tags': []
        }
        res = self.client.post(LIST_POST_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        categories = Category.objects.all()
        self.assertEqual(categories.count(), 2)
        for category in payload['categories']:
            exists = Category.objects.filter(
                user=self.user,
                name=category['name']
            ).exists()
            self.assertTrue(exists)

    def test_create_post_with_existing_categories(self):
        """Test creating post with existing
        category without creating it again."""
        category = Category.objects.create(user=self.user, name='Development')
        payload = {
            'title': 'Sample title',
            'content': 'Sample content',
            'published_date': "2023-10-12T16:48:32.691Z",
            'categories': [
                {'name': 'Development'}, {'name': 'Sample category'}
                ],
            'tags': []
        }
        res = self.client.post(LIST_POST_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        posts = Post.objects.filter(author=self.profile)
        self.assertEqual(posts.count(), 1)
        post = posts[0]
        self.assertEqual(post.categories.count(), 2)
        self.assertIn(category, post.categories.all())
        for category in payload['categories']:
            exists = Category.objects.filter(
                user=self.user,
                name=category['name']
            ).exists()
            self.assertTrue(exists)

    def test_create_categories_while_updating_posts(self):
        """Test creating categories while updating posts."""
        payload = {
            'categories': [{'name': 'Sample category'}]
        }
        post = create_post(author=self.profile)
        url = post_detail_url(post.id)

        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        post_categories = post.categories.all()
        self.assertEqual(post_categories.count(), 1)
        new_category = Category.objects.get(
            user=self.user,
            name=(payload['categories'][0])['name']
        )
        self.assertIn(new_category, Category.objects.all())

    def test_update_post_assign_categories(self):
        """Test assigning an existing category when updating a post."""
        sample_category = Category.objects.create(
            user=self.user, name='Sample'
        )
        sample2_category = Category.objects.create(
            user=self.user, name='Sample2'
        )
        sample_post = create_post(author=self.profile)
        sample_post.categories.add(sample_category)
        payload = {
            'categories': [{'name': 'Sample2'}]
        }

        url = post_detail_url(sample_post.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        sample_post.refresh_from_db()
        self.assertIn(sample2_category, sample_post.categories.all())
        self.assertNotIn(sample_category, sample_post.categories.all())

    def test_clear_categories_while_updating_posts(self):
        """Test clearing all categories of a post while updating it."""
        sample_post = create_post(author=self.profile)
        url = post_detail_url(sample_post.id)
        sample_category = Category.objects.create(
            user=self.user, name='Sample'
        )
        sample_post.categories.add(sample_category)
        payload = {'categories': []}

        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        post_categories = sample_post.categories.all()
        self.assertEqual(post_categories.count(), 0)
        self.assertTrue(Category.objects.filter(
            user=self.user, name='Sample'
        ).exists())

    def test_create_post_with_creating_new_tags(self):
        """Test creating posts with new tags."""
        payload = {
            'title': 'Sample title',
            'content': 'Sample content',
            'published_date': "2023-10-12T16:48:32.691Z",
            'categories': [],
            'tags': [
                {'name': 'Development'}, {'name': 'Sample tag'}
                ]
        }
        res = self.client.post(LIST_POST_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        tags = Tag.objects.all()
        self.assertEqual(tags.count(), 2)
        for tag in payload['tags']:
            exists = Tag.objects.filter(
                user=self.user,
                name=tag['name']
            ).exists()
            self.assertTrue(exists)

    def test_create_post_with_existing_tags(self):
        """Test creating post with existing
        tag without creating it again."""
        tag = Tag.objects.create(user=self.user, name='Development')
        payload = {
            'title': 'Sample title',
            'content': 'Sample content',
            'published_date': "2023-10-12T16:48:32.691Z",
            'categories': [],
            'tags': [
                {'name': 'Development'}, {'name': 'Sample category'}
                ]
        }
        res = self.client.post(LIST_POST_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        posts = Post.objects.filter(author=self.profile)
        self.assertEqual(posts.count(), 1)
        post = posts[0]
        self.assertEqual(post.tags.count(), 2)
        self.assertIn(tag, post.tags.all())
        for tag in payload['tags']:
            exists = Tag.objects.filter(
                user=self.user,
                name=tag['name']
            ).exists()
            self.assertTrue(exists)

    def test_create_tags_while_updating_posts(self):
        """Test creating tags while updating posts."""
        payload = {
            'tags': [{'name': 'Sample tag'}]
        }
        post = create_post(author=self.profile)
        url = post_detail_url(post.id)

        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        post_tags = post.tags.all()
        self.assertEqual(post_tags.count(), 1)
        new_tag = Tag.objects.get(
            user=self.user,
            name=(payload['tags'][0])['name']
        )
        self.assertIn(new_tag, Tag.objects.all())

    def test_update_post_assign_tags(self):
        """Test assigning an existing tag when updating a post."""
        sample_tag = Tag.objects.create(
            user=self.user, name='Sample'
        )
        sample2_tag = Tag.objects.create(
            user=self.user, name='Sample2'
        )
        sample_post = create_post(author=self.profile)
        sample_post.tags.add(sample_tag)
        payload = {
            'tags': [{'name': 'Sample2'}]
        }

        url = post_detail_url(sample_post.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        sample_post.refresh_from_db()
        self.assertIn(sample2_tag, sample_post.tags.all())
        self.assertNotIn(sample_tag, sample_post.tags.all())

    def test_clear_tags_while_updating_posts(self):
        """Test clearing all tags of a post while updating it."""
        sample_post = create_post(author=self.profile)
        url = post_detail_url(sample_post.id)
        sample_tag = Tag.objects.create(
            user=self.user, name='Sample'
        )
        sample_post.tags.add(sample_tag)
        payload = {'tags': []}

        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        post_tags = sample_post.tags.all()
        self.assertEqual(post_tags.count(), 0)
        self.assertTrue(Tag.objects.filter(
            user=self.user, name='Sample'
        ).exists())


class PostImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='example@gmail.com', password='T123@example'
            )
        self.client.force_authenticate(self.user)
        self.profile = Profile.objects.get(user=self.user)
        self.post = create_post(author=self.profile)

    def tearDown(self):
        self.post.image.delete()

    def test_uploading_an_image_to_post_successfully(self):
        """Test uploading an image to a sample
        post successfully with response 200."""
        url = image_upload_url(self.post.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            image = Image.new('RGB', (10, 10))
            image.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'image': image_file}
            res = self.client.post(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.post.image.path))

    def test_uploading_image_with_invalid_data(self):
        """Test uploading posts images with invalid
        data unsuccessfully with response 400."""
        url = image_upload_url(self.post.id)
        payload = {'image': 'invalid_data'}

        res = self.client.post(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
