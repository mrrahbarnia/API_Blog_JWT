"""
Serializers for the user API's.
"""
from django.core import exceptions
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import (
    get_user_model,
    authenticate
)
from django.utils.translation import gettext as _

from rest_framework import serializers


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for validating and convert into
    Json format for user registration endpoint.
    """
    email = serializers.EmailField(max_length=100)
    password = serializers.CharField(min_length=8, write_only=True)
    password1 = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ["email", "password", "password1"]

    def validate(self, attrs):
        """To validate attrs."""
        email = attrs.get('email')
        password = attrs.get('password')
        password1 = attrs.get('password1')

        user = get_user_model().objects.filter(email=email).exists()
        if user:
            raise serializers.ValidationError(
                {"detail": "Email already exists"}
            )
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
        return get_user_model().objects.create_user(**validated_data)


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
