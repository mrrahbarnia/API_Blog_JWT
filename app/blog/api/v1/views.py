"""
Views for Blog Endpoint's API's.
"""
from django.contrib.auth import get_user_model

from rest_framework import viewsets
from rest_framework import permissions

from core.models import (
    Post,
    Profile,
    Category,
    Tag,
    Comment
)
from .permissions import (
    IsOwnerOrReadOnlyProfile,
    IsOwnerOrReadOnlyUser,
)
from .serializers import (
    PostSerializer,
    PostDetailSerializer,
    CategorySerializer,
    TagSerializer,
    CommentSerializer,
    CommentDetailSerializer
)


class PostModelViewSet(viewsets.ModelViewSet):
    """CRUD for post's endpoints."""
    serializer_class = PostDetailSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnlyProfile
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
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnlyUser
        ]

    def perform_create(self, serializer):
        """Select user from request."""
        user = get_user_model().objects.get(id=self.request.user.id)
        serializer.save(user=user)


class TagModelViewSet(viewsets.ModelViewSet):
    """CRUD for tags endpoints."""
    serializer_class = TagSerializer
    queryset = Tag.objects.all().order_by('-name')
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnlyUser
    ]

    def perform_create(self, serializer):
        """Select user from request."""
        user = get_user_model().objects.get(id=self.request.user.id)
        serializer.save(user=user)


class CommentModelViewSet(viewsets.ModelViewSet):
    """CRUD for comments endpoints."""
    serializer_class = CommentDetailSerializer
    queryset = Comment.objects.all().order_by('-comment')
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnlyUser
    ]

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)

    def get_serializer_class(self):
        if self.action == 'list':
            return CommentSerializer
        return CommentDetailSerializer
