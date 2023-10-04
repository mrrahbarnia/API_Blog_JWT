"""
Views for the user API's.
"""
from django.contrib.auth import get_user_model

from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework import (
    generics,
    # authentication,
    permissions
)

from .serializers import (
    UserRegistrationSerializer,
    GenerateAuthTokenSerializer,
    ChangePasswordSerializer
)


class UserRegistrationApiView(generics.CreateAPIView):
    """Endpoint for registrating users."""
    serializer_class = UserRegistrationSerializer


class GenerateAuthTokenApiView(ObtainAuthToken):
    """Endpoint for generating token for auhenticated users."""
    serializer_class = GenerateAuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ChangepasswordApiView(generics.GenericAPIView):
    """Endpoint for updating user's password."""
    serializer_class = ChangePasswordSerializer
    model = get_user_model()
    # authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Function for retrieving and
        returning authenticated users."""
        return self.request.user

    def put(self, request, *args, **kwargs):
        """PUT method for updating password."""
        self.object = self.get_object()
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not self.object.check_password(serializer.data.get('old_password')):
            return Response(
                {"old_password": "Wrong password."},
                status=status.HTTP_400_BAD_REQUEST)
        self.object.set_password(serializer.data.get('new_password'))
        self.object.save()
        return Response({"detail": "Password changed successfully"},
                        status=status.HTTP_200_OK)
