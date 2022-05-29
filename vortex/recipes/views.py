from django.contrib.auth.models import User
from django.db.models import Avg, Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from recipes.serializers import RegisterSerializer, RecipeSerializer, RateSerializer, IngredientSerializer
from recipes.models import Recipe, Ingredient
from recipes.filters import MinMaxFilterBackend


# Create your views here.
class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class RecipeViewSet(ModelViewSet):
    """
    Viewset for anything related to Recipes.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = RecipeSerializer
    filter_backends = [DjangoFilterBackend, MinMaxFilterBackend]
    filterset_fields = ['name', 'text', 'ingredients__name']
    queryset = Recipe \
        .objects \
        .select_related('user') \
        .prefetch_related('ratings') \
        .prefetch_related('recipe_ratings') \
        .annotate(avg_rating=Avg('recipe_ratings__rate')) \
        .order_by('-id')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'], url_path='rate', url_name='rate')
    def rate(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = RateSerializer(data=request.data, context={'recipe': obj, 'user': request.user})
        serializer.is_valid(raise_exception=True)
        obj.update_rating(request.user, serializer.validated_data['rate'])
        return Response()

    @action(detail=False, url_path='mine', url_name='mine')
    def mine(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().filter(user=request.user))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class IngredientsAPIView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.annotate(Count('recipes')).order_by('-recipes__count')[:5]
