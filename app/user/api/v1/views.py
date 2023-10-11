"""
Views for the user API's.
"""
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import get_user_model

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.settings import api_settings
from rest_framework import (
    generics,
    authentication,
    permissions
)

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
import jwt
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidSignatureError
)

from core.models import Profile
from app.celery_config import send_email_activation_account
from app.celery_config import send_email_reset_password
from .serializers import (
    UserRegistrationSerializer,
    GenerateAuthTokenSerializer,
    ChangePasswordSerializer,
    CustomJwtSerializer,
    ProfileSerializer,
    ResendActivationSerializer,
    ResetPasswordEmailRequestSerializer,
    ResetPasswordValidateTokenSerializer,
    SetNewPasswordSerializer
)


class UserRegistrationApiView(generics.GenericAPIView):
    """Endpoint for registrating users."""
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        """Sending activation email for registrated
        users just after registration."""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        email = serializer.validated_data['email']
        user_obj = get_user_model().objects.get(email=email)
        token = self.get_tokens_for_user(user_obj)
        current_site = str(
            get_current_site(request=request).domain
            ) + '/user/api/v1/activation/confirm'
        abs_url = 'http://'+current_site+'/'+str(token)

        send_email_activation_account.apply_async(
            kwargs={'email': email, 'context': abs_url}
            )

        return Response(
            {'detail': 'Verfification email was sent for you.'},
            status=status.HTTP_201_CREATED
            )

    def get_tokens_for_user(self, user):
        """Generating jwt for sending verification email after signing up."""
        refresh = RefreshToken.for_user(user)

        return str(refresh.access_token)


class GenerateAuthTokenApiView(ObtainAuthToken):
    """Endpoint for generating token for auhenticated users."""
    serializer_class = GenerateAuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'email': user.email,
            'user_id': user.pk
        })


class DestroyAuthTokenApiView(APIView):
    """Endpoint for destroying auth token."""
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def post(self, request):
        """POST method for destroying auth token."""
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangepasswordApiView(generics.GenericAPIView):
    """Endpoint for updating user's password."""
    serializer_class = ChangePasswordSerializer
    model = get_user_model()
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


class CustomJwtCreateView(TokenObtainPairView):
    """Custom view based on TokenObtainPairView class
    for showing email and id in addition."""
    serializer_class = CustomJwtSerializer


class ProfileApiView(generics.RetrieveUpdateAPIView):
    """Retrieving and updating profiles by authenticated user."""
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Profile.objects.all()

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.queryset.get(user=self.request.user)


class ActivationApiView(APIView):
    """Getting activation email and check
    the token whether is valid or not."""
    def get(self, request, token, *args, **kwargs):
        User = get_user_model()
        try:
            decoded_jwt = jwt.decode(
                token, settings.SECRET_KEY, algorithms=['HS256']
            )
            user_id = decoded_jwt.get('user_id')
            try:
                user_obj = User.objects.get(id=user_id)
                user_obj.is_verified = True
                user_obj.save()
                return Response({
                    'detail': 'Your account is verifed now.'},
                    status=status.HTTP_200_OK
                )
            except User.DoesNotExist:
                return Response({'detail': 'Token is invalid.'})

        except ExpiredSignatureError:
            return Response({'detail': 'Token has been expired.'})
        except InvalidSignatureError:
            return Response({'detail': 'Token is invalid.'})


class ResendActivationApiView(generics.GenericAPIView):
    """For resending activation email."""
    serializer_class = ResendActivationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        user_obj = get_user_model().objects.get(email=email)
        token = self.get_tokens_for_user(user_obj)
        current_site = str(
            get_current_site(request=request).domain
            ) + '/user/api/v1/activation/confirm'
        abs_url = 'http://'+current_site+'/'+str(token)

        send_email_activation_account.apply_async(
            kwargs={'email': email, 'context': abs_url}
            )
        return Response({
            'detail': 'Verfification email was sent for you.'},
            status=status.HTTP_200_OK
        )

    def get_tokens_for_user(self, user):
        """Generating jwt for sending verification email after signing up."""
        refresh = RefreshToken.for_user(user)

        return str(refresh.access_token)


class ResetPasswordRequestEmailApiView(generics.GenericAPIView):
    """Reseting password by getting email address and sending an email."""
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        user_obj = get_user_model().objects.get(email=email)
        token = RefreshToken.for_user(user_obj)
        current_site = str(
            get_current_site(request=request).domain
            )+'/user/api/v1/reset-password/validate-token/'
        link = 'http://'+current_site

        send_email_reset_password.apply_async(kwargs={
            'email': email, 'token': str(token.access_token), 'link': link
            })
        return Response({
            'detail': 'Reset password email was sent for you.'},
            status=status.HTTP_200_OK
        )


class ResetPasswordValidateTokenApiView(generics.GenericAPIView):
    """Validating obtained token."""
    serializer_class = ResetPasswordValidateTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(
            {'detail': 'Token is valid.'},
            status=status.HTTP_200_OK
            )


class SetNewPasswordSerializer(generics.GenericAPIView):
    """Setting new password for a user."""
    serializer_class = SetNewPasswordSerializer

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({
            'detail': 'Password changed.'
        })
