"""
Models.
"""
import os
import uuid

from django.conf import settings
from django.utils.text import Truncator
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager
)
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save

from app.models import TimeStampedModel


def post_image_file_path(instance, filename):
    """Create and return a path for saving images."""
    ext = os.path.splitext(filename)[1]
    file_name = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'post', file_name)


class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a new user with the given email and password."""
        if not email:
            raise ValueError(_("The email must be set."))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """
        Create and save a SuperUser with the given email and password.
        """
        user = self.create_user(email, password)
        user.is_verified = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, TimeStampedModel, PermissionsMixin):
    """Custom User model to use email instead of username."""
    email = models.EmailField(
        _("email address"), max_length=100, unique=True
        )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'

    objects = UserManager()

    def __str__(self):
        return self.email


SEX = [
    ("M", "male"),
    ("F", "female")
]


class Profile(TimeStampedModel):
    """This class defines profile attributes."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    bio = models.TextField()
    sex = models.CharField(choices=SEX, max_length=4)

    def __str__(self):
        return self.user.email


@receiver(post_save, sender=User)
def save_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


class Post(TimeStampedModel):
    """This class defines posts attributes."""
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    image = models.ImageField(null=True, upload_to=post_image_file_path)
    title = models.CharField(max_length=255)
    content = models.TextField()
    categories = models.ManyToManyField('Category')
    tags = models.ManyToManyField('Tag')
    comments = models.ManyToManyField('Comment')
    status = models.BooleanField(default=False)
    counted_views = models.IntegerField(default=0)
    published_date = models.DateTimeField()

    def content_snippet(self):
        """Return a snippet of content."""
        truncated_content = Truncator(self.content).words(5)
        return truncated_content

    def __str__(self):
        return self.title


class Category(TimeStampedModel):
    """This class defines categories attributes."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Tag(TimeStampedModel):
    """This class defines tags attributes."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Comment(TimeStampedModel):
    """This class defines comments attributes."""
    post_obj = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    comment = models.TextField(max_length=1000)

    def __str__(self):
        return f'from: {self.user} - on: {self.post_obj}'

    def comment_snippet(self):
        """Return a snippet of the comment."""
        trancated_comment = Truncator(self.comment).words(5)
        return trancated_comment
