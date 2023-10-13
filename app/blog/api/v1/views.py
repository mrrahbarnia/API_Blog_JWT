"""
Views for Blog Endpoint's API's.
"""
from django.contrib.auth import get_user_model

from rest_framework import viewsets
from rest_framework import permissions

from core.models import (
    Post,
    Profile,
    Category
)
from .permissions import (
    IsOwnerOrReadOnlyForPost,
    IsOwnerOrReadOnlyForCategory
)
from .serializers import (
    PostSerializer,
    PostDetailSerializer,
    CategorySerializer
)


class PostModelViewSet(viewsets.ModelViewSet):
    """CRUD for post's endpoints."""
    serializer_class = PostDetailSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnlyForPost
        ]
    queryset = Post.objects.filter(status=True).order_by('-id')

    def perform_create(self, serializer):
        profile = Profile.objects.get(user=self.request.user)
        serializer.save(author=profile)

    def get_serializer_class(self):
        """Retrieving various serializers for various methods."""
        if self.action == 'list':
            return PostSerializer
        return PostDetailSerializer


class CategoryModelViewSet(viewsets.ModelViewSet):
    """CRUD for categories endpoints."""
    serializer_class = CategorySerializer
    queryset = Category.objects.all().order_by('-name')
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnlyForCategory
        ]

    def perform_create(self, serializer):
        user = get_user_model().objects.get(id=self.request.user.id)
        serializer.save(user=user)
