"""
Views for the user API's.
"""
from rest_framework import generics

from .serializers import UserRegistrationSerializer


class UserRegistrationApiView(generics.CreateAPIView):
    """Endpoint for registrating users."""
    serializer_class = UserRegistrationSerializer
    # def post(self, request, *args, **kwargs):
    #     serializer = self.serializer_class
    #     serializer.
