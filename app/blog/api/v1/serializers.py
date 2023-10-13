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

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'title', 'snippet', 'content', 'abs_url'
            ]
        read_only_fields = ['id', 'author', 'status']
        extra_kwargs = {
            'content': {'write_only': True}
        }

    def create(self, validated_data):
        """Create and return a post with validated data."""
        post = Post.objects.create(**validated_data)
        return post

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
