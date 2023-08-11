"""
Tests for the user API
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    """Helper function to create a new user"""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users API (public)"""
    def setUp(self):
        self.client = APIClient()
    def test_create_user_success(self):
        """Test creating user with valid payload is successful"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)  # Check if the user was created
        user = get_user_model().objects.get(email=payload['email'])  # Check if the user exists
        self.assertTrue(user.check_password(payload['password']))  # Check if the password is correct
        self.assertNotIn('password', res.data)  # Check if the password is not returned in the response

    def test_user_with_imail_exists_error(self):
        """Test creating a user that already exists"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)  # Check if the user was not created

    def test_password_too_short_error(self):
        """Test that the password must be more than 5 characters"""
        payload = {
            'email': 'test@example.com',
            'password': 'pw',
            'name': 'Test Name',
        }
        res = self.client.post(CREATE_USER_URL, payload)  # Create the user

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)  # Check if the user was not created
        user_exists = get_user_model().objects.filter(
            email=payload['email']).exists()  # Check if the user exists
        self.assertFalse(user_exists)  # Check if the user does not exist

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        user_details = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'test-user-pass123',
        }
        create_user(**user_details)  # Create the user

        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }
        res = self.client.post(TOKEN_URL, payload)  # Create the token

        self.assertIn('token', res.data)  # Check if the token was created
        self.assertEqual(res.status_code, status.HTTP_200_OK)  # Check if the token was created

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        create_user(email='test@example.com', password='goodpass')
        payload = {'email': 'test@example.com', 'password': 'wrongpass'}
        res = self.client.post(TOKEN_URL, payload)  # Create the token

        self.assertNotIn('token', res.data)  # Check if the token was not created
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)  # Check if the token was not created

    def test_create_token_blank_password(self):
        """Test that token is not created if password is blank"""
        payload = {'email': 'test@example.com', 'password': ''}
        res = self.client.post(TOKEN_URL, payload)  # Create the token

        self.assertNotIn('token', res.data)  # Check if the token was not created
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)  # Check if the token was not created

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)  # Check if the user is not authenticated

class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication"""
    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)  # Authenticate the user

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)  # Check if the user is authenticated
        self.assertEqual(res.data, {  # Check if the user data is correct
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the me url"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        payload = {
            'name': 'New Name',
            'password': 'newtestpass123',
        }
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()  # Refresh the user object
        self.assertEqual(self.user.name, payload['name'])  # Check if the name was updated
        self.assertTrue(self.user.check_password(payload['password']))  # Check if the password was updated
        self.assertEqual(res.status_code, status.HTTP_200_OK)  # Check if the user was updated
