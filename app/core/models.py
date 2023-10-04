from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager
)
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save

from app.models import TimeStampedModel


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
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    image = models.ImageField(blank=True, null=True)
    first_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    bio = models.TextField()
    sex = models.CharField(choices=SEX, max_length=4)

    def __str__(self):
        self.user.email


@receiver(post_save, sender=get_user_model())
def save_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)