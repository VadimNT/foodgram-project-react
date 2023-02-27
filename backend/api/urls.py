from django.urls import path, include
from rest_framework.routers import DefaultRouter

from backend.api.serializers import (IngredientViewSet, RecipeViewSet,
                                     TagViewSet, UserViewSet, )

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register(r'users', UserViewSet, 'users')
router_v1.register(r'tags', TagViewSet, 'tags')
router_v1.register(r'recipes', RecipeViewSet, 'recipes')
router_v1.register(r'ingredients', IngredientViewSet, 'ingredients')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/', include('djoser.urls')),
    path('v1/', include('djoser.urls.jwt')),
]
