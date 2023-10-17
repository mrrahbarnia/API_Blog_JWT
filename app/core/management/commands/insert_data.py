"""
Command for inserting fake data via faker module into the database.
"""
from faker import Faker
import random
from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from core.models import (
    Profile,
    Post,
    Category,
    Tag
)

categories = [
    'Django',
    'Programming',
    'IT',
    'Python',
    'DRF'
]

tags = [
    'Useful',
    'Expensive',
    'Cheap',
    'Hardwork',
    'Mentally'
]


class Command(BaseCommand):
    """Django command to inserting fake data."""

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.fake = Faker()

    def handle(self, *args, **options):
        """Entrypoint for command."""
        fake_user = get_user_model().objects.create_user(
            email=self.fake.email(), password='T123@example', is_verified=True
        )
        fake_profile = Profile.objects.get(user=fake_user)
        fake_profile.first_name = self.fake.first_name()
        fake_profile.last_name = self.fake.last_name()
        fake_profile.bio = self.fake.paragraph(nb_sentences=3)
        fake_profile.sex = random.choice(['M', 'F'])
        fake_profile.save()

        for category in categories:
            Category.objects.get_or_create(user_id=1, name=category)

        for tag in tags:
            Tag.objects.get_or_create(user_id=1, name=tag)

        for _ in range(10):
            """Create and return 10 posts each time."""
            post = Post.objects.create(
                author=fake_profile,
                title=self.fake.paragraph(nb_sentences=1),
                content=self.fake.paragraph(nb_sentences=5),
                status=random.choice([True, False]),
                published_date=datetime.now()
            )
            post.save()
            category = Category.objects.get(name=random.choice(categories))
            tag = Tag.objects.get(name=random.choice(tags))
            post.categories.add(category)
            post.tags.add(tag)
            post.refresh_from_db()
