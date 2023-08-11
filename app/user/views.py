"""
Vews for user API
"""
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from . import serializers


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = serializers.UserSerializer  # Set the serializer class


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for the user"""
    serializer_class = serializers.AuthTokenSerializer
    # Set the renderer so that we can view the endpoint in the browser
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES # Get the default renderer classes


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""
    serializer_class = serializers.UserSerializer  # Set the serializer class
    authentication_classes = (authentication.TokenAuthentication,)  # Set the authentication classes
    permission_classes = (permissions.IsAuthenticated,)  # Set the permission classes

    def get_object(self):
        """Retrieve and return authenticated user"""
        return self.request.user  # Return the authenticated user