from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.pagination import CustomPagination
from api.permissions import (IsAdminOrReadOnly,
                             IsAuthenticated,
                             IsAuthorOrAdminOrReadOnly, )
from api.serializers import (CartSerializer, IngredientSerializer,
                             RecipeReadSerializer, RecipeShortSerializer,
                             RecipeWriteSerializer, SubscribeSerializer,
                             TagSerializer, UserPasswordSerializer,
                             UserSerializer, )
from recipes.models import (Cart, Favorite, Ingredient, IngredientRecipe,
                            Recipe, Tag, )
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

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,),
    )
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
        permission_classes=(IsAuthenticated,)
    )
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

    def set_status_favorite(self, request, target):
        obj = get_object_or_404(Recipe, pk=self.kwargs[self.lookup_field])
        if request.method == "POST":
            instance, created = target.objects.get_or_create(
                user=request.user, recipe=obj
            )
            if not created:
                return Response(
                    {"errors": "Ошибка подписки"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = RecipeShortSerializer(obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            target.objects.filter(user=request.user, recipe=obj).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @action(
        detail=True,
        permission_classes=[IsAuthorOrAdminOrReadOnly],
        methods=["POST", "DELETE"],
    )
    def favorite(self, request, *args, **kwargs):
        """Добавление и удаление из избранных"""
        return self.set_status_favorite(request, Favorite)


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
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['POST'],
        permission_classes=(IsAuthenticated,),
    )
    def set_password(self, request):
        """Изменить пароль."""

        serializer = UserPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Пароль изменен!'},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {'error': 'Введите верные данные!'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
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
