"""
Permissions for Blog endpoints.
"""
from rest_framework import permissions


class IsOwnerOrReadOnlyProfile(permissions.BasePermission):
    """Permission for deleting and updating a post
    only with the author of that post otherwise readonly."""

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.author.user.id == request.user.id


class IsOwnerOrReadOnlyUser(permissions.BasePermission):
    """Permission for deleting and updating a category
    only with the user of that category otherwise readonly."""

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user.id == request.user.id
