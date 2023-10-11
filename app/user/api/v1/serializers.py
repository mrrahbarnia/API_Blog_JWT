"""
Serializers for the user API's.
"""
from django.conf import settings
from django.core import exceptions
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext as _
from django.contrib.auth import (
    get_user_model,
    authenticate
)

from rest_framework import serializers

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import jwt
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidSignatureError
)

from core.models import Profile

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for validating and convert into
    Json format for user registration endpoint.
    """
    password1 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "password1"]
        extra_kwargs = {'password': {'min_length': 8, 'write_only': True}}

    def validate(self, attrs):
        """To validate attrs."""
        password = attrs.get('password')
        password1 = attrs.get('password1')

        if password != password1:
            raise serializers.ValidationError(
                {"detail": "Passwords must be match."}
            )

        errors = dict()
        try:
            validate_password(password)
        except exceptions.ValidationError as e:
            errors['password'] = list(e.messages)
        if errors:
            raise serializers.ValidationError(errors)

        return super(UserRegistrationSerializer, self).validate(attrs)

    def create(self, validated_data):
        """Create the user with encrypted password."""
        validated_data.pop("password1", None)
        return User.objects.create_user(**validated_data)


class GenerateAuthTokenSerializer(serializers.Serializer):
    """Serializer for generating auth token for each users."""
    email = serializers.EmailField(max_length=100)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        """Validating payload for checking whether the user exists or not."""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            msg = _("Unable to authenticate with provided credentials.")
            raise serializers.ValidationError(msg, code="authorization")

        if not user.is_verified:
            raise serializers.ValidationError(
                {'detail': 'User is not verified.'}
            )

        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for retrieve new passwords,
    validate and save them istead of old password"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True)

    def validate(self, attrs):
        """Validating new passwords."""
        new_password = attrs.get('new_password')
        new_password1 = attrs.get('new_password1')
        if new_password != new_password1:
            raise serializers.ValidationError(
                {"detail": "Passwords must be match."}
            )

        errors = dict()
        try:
            validate_password(new_password)
        except exceptions.ValidationError as e:
            errors['new_password'] = list(e.messages)
        if errors:
            raise serializers.ValidationError(errors)
        attrs['old_password']
        attrs['new_password']

        return attrs


class CustomJwtSerializer(TokenObtainPairSerializer):
    """Custom serializer based on TokenObtainPairSerializer
    to showing user's email and user's id"""

    def get_token(cls, user):
        """Showing user'e email on decoding token."""
        token = super().get_token(user)
        token['email'] = user.email
        return token

    def validate(self, attrs):
        """Return email and id in addition of other details."""
        validated_data = super().validate(attrs)
        if not self.user.is_verified:
            raise serializers.ValidationError(
                {'detail': 'User is not verified.'}
            )
        validated_data['email'] = self.user.email
        validated_data['id'] = self.user.id

        return validated_data


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for Profile model."""
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'email', 'first_name', 'last_name', 'bio', 'sex']
        extra_kwargs = {'id': {'read_only': True}}


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    """Serializer for reset password."""
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        """Validating for whether the email exists or not."""
        email = attrs.get('email')
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                'detail': 'There is no user with provided email.'
            })

        return super().validate(attrs)


class ResendActivationSerializer(serializers.Serializer):
    """Serializer for resend activation endpoint."""
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        """Validating for whether the email exists or not and
        whether the user with provided email is verified or not."""
        email = attrs.get('email')
        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                'detail': 'There is no user with provided email.'
            })
        if user_obj.is_verified:
            raise serializers.ValidationError({
                'detail': 'The user has been already verified.'
            })
        attrs['user'] = user_obj

        return super().validate(attrs)


class ResetPasswordValidateTokenSerializer(serializers.Serializer):
    """Serializing and validating obtained token."""
    token = serializers.CharField(max_length=600)

    def validate(self, attrs):
        """Validating token."""
        token = attrs.get('token')
        try:
            jwt.decode(
                token, settings.SECRET_KEY, algorithms=['HS256']
            )
        except InvalidSignatureError:
            raise serializers.ValidationError({
                'detail': 'Token is invalid.'
            })
        except ExpiredSignatureError:
            raise serializers.ValidationError({
                'detail': 'Token has been expired.'
            })

        return super().validate(attrs)


class SetNewPasswordSerializer(serializers.Serializer):
    """Setting new password."""
    token = serializers.CharField(max_length=600)
    new_password = serializers.CharField(min_length=8)
    confirmation_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """"""
        token = attrs.get('token')
        password = attrs.get('new_password')
        password1 = attrs.get('confirmation_password')
        try:
            decoded_token = jwt.decode(
                token, settings.SECRET_KEY, algorithms=['HS256']
            )
        except InvalidSignatureError:
            raise serializers.ValidationError({
                'detail': 'Token is invalid.'
            })
        except ExpiredSignatureError:
            raise serializers.ValidationError({
                'detail': 'Token has been expired.'
            })
        try:
            user_obj = User.objects.get(id=decoded_token.get('user_id'))
        except User.DoesNotExist:
            raise serializers.ValidationError({
                'detail': 'Token is invalid.'
            })

        if password != password1:
            raise serializers.ValidationError(
                {"detail": "Passwords must be match."}
            )

        errors = dict()
        try:
            validate_password(password)
        except exceptions.ValidationError as e:
            errors['password'] = list(e.messages)
        if errors:
            raise serializers.ValidationError(errors)

        user_obj.set_password(password)
        user_obj.save()
        return super().validate(attrs)
