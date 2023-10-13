"""
Serializers for blog endpoints.
"""
from rest_framework import serializers

from core.models import (
    Post,
    Category
)


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for categories."""

    class Meta:
        model = Category
        fields = ['id', 'name']
        read_only_fields = ['id']


class PostSerializer(serializers.ModelSerializer):
    """Serializer for posts."""
    snippet = serializers.CharField(source='content_snippet', read_only=True)
    abs_url = serializers.SerializerMethodField(read_only=True)
    categories = CategorySerializer(many=True, required=True)

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'title', 'snippet',
            'categories', 'content', 'abs_url'
            ]
        read_only_fields = ['id', 'author', 'status']
        extra_kwargs = {
            'content': {'write_only': True}
        }

    def _get_or_create_categories(self, categories, post):
        """Handle getting or creating categories and
        assign them to post while creating them."""
        auth_user = self.context['request'].user
        for category in categories:
            category_obj, created = Category.objects.get_or_create(
                user=auth_user,
                # Best practice for future updates of Category model.
                **category
            )
            post.categories.add(category_obj)

    def create(self, validated_data):
        """Create and return a post with validated data."""
        categories = validated_data.pop('categories', [])
        post = Post.objects.create(**validated_data)
        self._get_or_create_categories(categories, post)

        return post

    def update(self, instance, validated_data):
        """Update and return a post with validated data."""
        categories = validated_data.pop('categories', None)
        if categories is not None:
            instance.categories.clear()
            self._get_or_create_categories(categories, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def get_abs_url(self, obj):
        """Return absolute URL of each posts."""
        request = self.context.get('request')
        return request.build_absolute_uri(obj.id)


class PostDetailSerializer(PostSerializer):
    """Serializer for posts detail's."""

    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + [
            'content', 'created_at', 'updated_at', 'status', 'published_date'
            ]
        fields.remove('snippet')
        fields.remove('abs_url')
        extra_kwargs = {'content': {'write_only': False}}
