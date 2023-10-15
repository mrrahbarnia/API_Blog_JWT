"""
Serializers for blog endpoints.
"""
from rest_framework import serializers
from django.urls import reverse
from core.models import (
    Post,
    Category,
    Tag,
    Comment
)


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for categories."""

    class Meta:
        model = Category
        fields = ['id', 'name']
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class PostSerializer(serializers.ModelSerializer):
    """Serializer for posts."""
    snippet = serializers.CharField(source='content_snippet', read_only=True)
    abs_url = serializers.SerializerMethodField(read_only=True)
    categories = CategorySerializer(many=True, required=True)
    tags = TagSerializer(many=True, required=True)

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'title', 'snippet', 'categories',
            'content', 'abs_url', 'tags'
            ]
        read_only_fields = ['id', 'author', 'status']
        extra_kwargs = {
            'content': {'write_only': True}
        }

    def _get_or_create_tags(self, tags, post):
        """Handle getting or creating tags and
        assign them to post while creating them."""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                # Best practice for future updates of tag model.
                **tag
            )
            post.tags.add(tag_obj)

    def _get_or_create_categories(self, categories, post):
        """Handle getting or creating categories and
        assign them to post while creating them."""
        auth_user = self.context['request'].user
        for category in categories:
            category_obj, created = Category.objects.get_or_create(
                user=auth_user,
                # Best practice for future updates of category model.
                **category
            )
            post.categories.add(category_obj)

    def create(self, validated_data):
        """Create and return a post with validated data."""
        categories = validated_data.pop('categories', [])
        tags = validated_data.pop('tags', [])
        post = Post.objects.create(**validated_data)
        self._get_or_create_categories(categories, post)
        self._get_or_create_tags(tags, post)

        return post

    def update(self, instance, validated_data):
        """Update and return a post with validated data."""
        categories = validated_data.pop('categories', None)
        tags = validated_data.pop('tags', None)
        if categories is not None:
            instance.categories.clear()
            self._get_or_create_categories(categories, instance)

        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def get_abs_url(self, obj):
        """Return absolute URL of each posts."""
        request = self.context.get('request')
        return request.build_absolute_uri(
            reverse('blog:api-blog:post-detail', args=[obj.id])
            )


class PostDetailSerializer(PostSerializer):
    """Serializer for posts detail's."""

    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + [
            'content', 'image', 'created_at',
            'updated_at', 'status', 'published_date'
            ]
        fields.remove('snippet')
        fields.remove('abs_url')
        extra_kwargs = {'content': {'write_only': False}}


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments."""
    snippet = serializers.CharField(source='comment_snippet', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'post_obj', 'snippet']
        read_only_fields = ['id', 'user']


class CommentDetailSerializer(CommentSerializer):
    """Serializer for detail comment."""

    class Meta(CommentSerializer.Meta):
        fields = CommentSerializer.Meta.fields + ['comment']
        fields.remove('snippet')


class ImageSerializer(serializers.ModelSerializer):
    """Serializer for the image belong to each posts."""

    class Meta:
        model = Post
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': True}}
