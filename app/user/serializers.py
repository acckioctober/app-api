"""
Serializers for user API Views
"""
from django.contrib.auth import (get_user_model,
                                 authenticate,)
from django.utils.translation import gettext as _
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""
    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')  # Fields that will be accepted in the request
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}  # Password will not be returned in the response

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)
        # **validated_data is the same as
        # email=validated_data['email'],
        # password=validated_data['password'],
        # name=validated_data['name']

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it"""
        password = validated_data.pop('password', None)  # Get the password from the validated data
        user = super().update(instance, validated_data)  # Update the user

        if password:
            user.set_password(password)  # Set the password
            user.save()  # Save the user
        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object"""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},  # Hide the password
        trim_whitespace=False  # Allow whitespace in the password
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),  # Get the request object
            username=email,
            password=password
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials.')
            raise serializers.ValidationError(msg, code='authorization')  # Raise an error if the user is not authenticated

        attrs['user'] = user  # Set the user in the attrs dictionary
        return attrs