from django.urls import path, include
from recipes.views import RegisterView, RecipeViewSet, IngredientsAPIView
from rest_framework.routers import DefaultRouter


app_name = 'app'

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='employees')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('most-used-ingredients/', IngredientsAPIView.as_view(), name='most_used_ingredients')
]
