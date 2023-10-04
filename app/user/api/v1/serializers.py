"""
Serializers for the user API's.
"""
from django.core import exceptions
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model

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
