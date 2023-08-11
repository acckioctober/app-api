"""
URL patterns for the user API
"""
from django.urls import path
from . import views


app_name = 'user'  # The app name is used to identify the app in the project

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),  # Create a new user
    path('token/', views.CreateTokenView.as_view(), name='token'),  # Create a new auth token for the user
    path('me/', views.ManageUserView.as_view(), name='me'),  # Manage the authenticated user
    ]
