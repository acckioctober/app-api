"""
URLs for recipe app
"""
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from recipe import views


router = DefaultRouter()  # Automatically generate URLs for viewset
router.register('recipes', views.RecipeViewSet)  # Register viewset with router

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls)),
]