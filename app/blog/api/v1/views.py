"""
Views for Blog Endpoint's API's.
"""
from rest_framework import viewsets
from rest_framework import permissions

from core.models import (
    Post,
    Profile
)
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    PostSerializer,
    PostDetailSerializer
)


class PostModelViewSet(viewsets.ModelViewSet):
    """CRUD for post's endpoints."""
    serializer_class = PostDetailSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly
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
