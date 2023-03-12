from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import CustomPagination
from api.permissions import (IsAdminOrReadOnly,
                             IsAuthorOrAdminOrReadOnly, IsAuthenticated)
from api.serializers import (TagSerializer, IngredientSerializer,
                             UserSerializer, SubscribeSerializer,
                             RecipeWriteSerializer, CartSerializer,
                             FavoriteSerializer, RecipeReadSerializer)
from recipes.models import Tag, Ingredient, Recipe, Favorite, Cart, \
    IngredientRecipe
from users.models import CustomUser, Follow


# Create your views here.
class TagViewSet(ModelViewSet):
    """Работает с тэгами.
       Изменение и создание тэгов разрешено только админам,
       остальным только разрешен просмотр
    """
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Tag.objects.all()


class IngredientViewSet(ModelViewSet):
    """
        Вывод ингридиентов.
    """
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Ingredient.objects.all()
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    """
        Вьюсет для работы с рецептами.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeWriteSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer

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
        ingredients = IngredientRecipe.objects.filter(
            recipe__carts__user=request.user
        ).order_by('ingredient__name').values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        return self.send_message(ingredients)

    @action(
        detail=True,
        methods=('POST',),
        permission_classes=(IsAuthenticated,))
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
        permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        instance, created = Recipe.objects.get_or_create(
            user=request.user, recipe=recipe
        )
        if not created:
            return Response(
                {"errors": "Ошибка подписки"},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = FavoriteSerializer(recipe)
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


class UserViewSet(ModelViewSet):
    """Работает с пользователями.
       ViewSet для работы с пользователми - вывод таковых,
       регистрация.
       Для авторизованных пользователей —
       возможность подписаться на автора рецепта.
    """
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()
    pagination_class = CustomPagination

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,),
        methods=['GET'],
        url_path='me',
    )
    def me(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, pk):
        user = self.request.user
        author = get_object_or_404(CustomUser, id=pk)
        if request.method == 'POST':
            if author == user:
                return Response(
                    {"errors": "Ошибка подписки"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            instance, created = Follow.objects.get_or_create(
                user=user,
                author=author
            )
            if not created:
                return Response(
                    {"errors": "Ошибка подписки"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = self.get_serializer(instance.author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            instance = Follow.objects.filter(
                user=self.request.user,
                author=author
            )
            if not instance.exists():
                return Response(
                    {"errors": "Ошибка отписки"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        user = request.user
        queryset = CustomUser.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(pages, many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)
