from datetime import datetime

from django.db.models import Q, F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from backend.api.filters import IngredientFilter
from backend.api.pagination import CustomPagination
from backend.api.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from backend.api.serializers import (TagSerializer, IngredientSerializer,
                                     UserSerializer, SubscribeSerializer,
                                     RecipeSerializer, CartSerializer,
                                     FavoriteSerializer)
from backend.foodgram.settings import DATE_TIME_FORMAT
from backend.recipes.models import Tag, Ingredient, Recipe, Favorite
from backend.users.models import User, Follow, Cart


# Create your views here.
class TagViewSet(ModelViewSet):
    """Работает с тэгами.
       Изменение и создание тэгов разрешено только админам,
       остальным только разрешен просмотр
    """
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Tag.objects.all()


class UserViewSet(ModelViewSet):
    """Работает с пользователями.
       ViewSet для работы с пользователми - вывод таковых,
       регистрация.
       Для авторизованных пользователей —
       возможность подписаться на автора рецепта.
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()
    pagination_class = CustomPagination

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, pk=id)

        if request.method == 'POST':
            serializer = SubscribeSerializer(
                author, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            get_object_or_404(Follow, user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        datail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(pages, many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(ModelViewSet):
    """
from recipes.models import Ingredient, Recipe, Tag
        Вывод ингридиентов.
    """
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    queryset = Ingredient.objects.all()
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    """
        Вьюсет для работы с рецептами.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)

    @staticmethod
    def send_message(ingredients):
        shopping_list = 'Купить в магазине:'
        for ingredient in ingredients:
            shopping_list += (
                f"\n{ingredient['ingredient__name']} "
                f"({ingredient['ingredient__measurement_unit']}) - "
                f"{ingredient['amount']}")
        file = 'shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{file}.txt"'
        return response

    @action(detail=False, methods=['GET'])
    def download_shopping_cart(self, request):
        """Загружает файл *.txt со списком покупок.
               Считает сумму ингредиентов в рецептах выбранных для покупки.
               Возвращает текстовый файл со списком ингредиентов.
               Вызов метода через url:  */recipes/download_shopping_cart/.
               Args:
                   request (WSGIRequest): Объект запроса..
               Returns:
                   Responce: Ответ с текстовым файлом.
               """
        user = self.request.user
        if not user.carts.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        filename = f'{user.username}_shopping_list.txt'
        shopping_list = [
            f'Список покупок для:\n\n{user.first_name}\n'
            f'{datetime.now().strftime(DATE_TIME_FORMAT)}\n'
        ]

        ingredients = Ingredient.objects.filter(
            recipe__recipe__in_carts__user=user
        ).values(
            'name',
            measurement=F('measurement_unit')
        ).annotate(amount=Sum('recipe__amount'))

        for ing in ingredients:
            shopping_list.append(
                f'{ing["name"]}: {ing["amount"]} {ing["measurement"]}'
            )
        shopping_list.append('\nПосчитано в Foodgram')
        shopping_list = '\n'.join(shopping_list)
        response = HttpResponse(
            shopping_list, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    @action(
        detail=True,
        methods=('POST',),
        permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        context = {'request': request}
        recipe = get_object_or_404(Recipe, id=pk)
        data = {
            'user': request.user.id,
            'recipe': recipe.id
        }
        serializer = CartSerializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def destroy_shopping_cart(self, request, pk):
        get_object_or_404(
            Cart,
            user=request.user.id,
            recipe=get_object_or_404(Recipe, id=pk)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('POST',),
        permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        context = {"request": request}
        recipe = get_object_or_404(Recipe, id=pk)
        data = {
            'user': request.user.id,
            'recipe': recipe.id
        }
        serializer = FavoriteSerializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def destroy_favorite(self, request, pk):
        get_object_or_404(
            Favorite,
            user=request.user,
            recipe=get_object_or_404(Recipe, id=pk)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def favorite(self, request, pk):
        return self._add_del_obj(pk, Favorite, Q(recipe__id=pk))
