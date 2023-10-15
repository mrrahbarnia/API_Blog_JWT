"""
Views for Blog Endpoint's API's.
"""
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiTypes
)

from django.contrib.auth import get_user_model

from rest_framework.filters import (
    SearchFilter,
    OrderingFilter
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import (
    viewsets,
    permissions,
    status
)

from django_filters.rest_framework import DjangoFilterBackend

from core.models import (
    Post,
    Profile,
    Category,
    Tag,
    Comment
)
from .paginations import Defaultpagination
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
    CommentDetailSerializer,
    ImageSerializer
)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='Comma seprated list of tag \
                IDs to filter posts by them.'
            ),
            OpenApiParameter(
                'categories',
                OpenApiTypes.STR,
                description='Comma seprated list of category \
                IDs to filter posts by them.'
            )
        ]
    )
)
class PostModelViewSet(viewsets.ModelViewSet):
    """CRUD for post's endpoints."""
    serializer_class = PostDetailSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnlyProfile
        ]
    queryset = Post.objects.filter(status=True).order_by('-id')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['categories', 'tags']
    search_fields = ['title', 'content']
    ordering_fields = ['published_date']
    pagination_class = Defaultpagination

    def _get_params_to_int(self, qs):
        """Convert comma seprated string to splited integers."""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        tags = self.request.query_params.get('tags')
        categories = self.request.query_params.get('categories')
        queryset = self.queryset
        if tags:
            tags_id = self._get_params_to_int(tags)
            queryset = queryset.filter(tags__id__in=tags_id)
        if categories:
            categories_id = self._get_params_to_int(categories)
            queryset = queryset.filter(categories__id__in=categories_id)
        return queryset.distinct()

    def perform_create(self, serializer):
        profile = Profile.objects.get(user=self.request.user)
        serializer.save(author=profile)

    def get_serializer_class(self):
        """Retrieving various serializers for various methods."""
        if self.action == 'list':
            return PostSerializer
        elif self.action == 'upload_image':
            return ImageSerializer
        return PostDetailSerializer

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """New method for uploading image for posts."""
        post_obj = self.get_object()
        serializer = self.get_serializer(post_obj, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
