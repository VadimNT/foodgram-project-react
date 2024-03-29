from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from drf_extra_fields.fields import Base64ImageField
from rest_framework.generics import get_object_or_404

from recipes.models import (Cart, Ingredient, IngredientRecipe, Recipe, Tag,
                            TagRecipe, )
from users.models import CustomUser


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """
        Првоеряем подписку на пользователя
            :param obj: пользователь, который подписан
            :return: вернет True or False, если подписан
        """
        request = self.context.get('request')
        if self.context.get('request').user.is_anonymous:
            return False
        return obj.following.filter(user=request.user).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """ Сериализатор создания пользователя """

    class Meta:
        model = CustomUser
        fields = (
            'email', 'username', 'first_name',
            'last_name', 'password')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class TagRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализтор для вывода тэгов в рецепте согласно Redoc.
    """

    class Meta:
        model = TagRecipe
        fields = ("id", "name", "color", "slug")
        read_only_fields = ("id", "name", "color", "slug",)

    def to_internal_value(self, data):
        if isinstance(data, int):
            return get_object_or_404(Tag, pk=data)
        return data


class IngredientSerializer(serializers.ModelSerializer):
    """
        Сериализатор для вывода ингридиентов.
    """

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """ Сериализатор ингридиентов и рецепта """
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeReadSerializer(serializers.ModelSerializer):
    """ Сериализатор просмотра рецепта """
    tags = TagSerializer(read_only=False, many=True)
    author = CustomUserSerializer(read_only=True, )
    ingredients = IngredientRecipeSerializer(
        many=True,
        source='ingredienttorecipe'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_ingredients(self, obj):
        ingredients = IngredientRecipe.objects.filter(recipe=obj)
        return IngredientRecipeSerializer(ingredients, many=True).data

    def get_is_favorited(self, recipe):
        """Проверка - находится ли рецепт в избранном.
            Args:
                recipe (Recipe): Переданный для проверки рецепт.
            Returns:
                bool: True - если рецепт в `избранном`
                у запращивающего пользователя, иначе - False.
        """
        request = self.context.get('request')

        if not request or request.user.is_anonymous:
            return False
        return recipe.favorited.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, recipe):
        """Проверка - находится ли рецепт в списке  покупок.
            Args:
                recipe (Recipe): Переданный для проверки рецепт.
            Returns:
                bool: True - если рецепт в `списке покупок`
            у запращивающего пользователя, иначе - False.
        """
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return recipe.carts.filter(user=request.user).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(many=True, )
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate_tags(self, tags):
        for tag in tags:
            if not Tag.objects.filter(id=tag.id).exists():
                raise serializers.ValidationError('Выбранный тег отсутствует')
        return tags

    def validate_cooking_time(self, cooking_time):
        if cooking_time < 1:
            raise serializers.ValidationError(
                'Время готовки должно быть не меньше одной минуты'
            )
        return cooking_time

    def validate_ingredients(self, ingredients):
        ingredients_list = []
        if not ingredients:
            raise serializers.ValidationError('Отсутствуют ингридиенты')
        for ingredient in ingredients:
            if ingredient['id'] in ingredients_list:
                raise serializers.ValidationError(
                    'Ингридиенты должны быть уникальными'
                )
            ingredients_list.append(ingredient['id'])
            if int(ingredient.get('amount')) < 1:
                raise serializers.ValidationError(
                    'Количество ингредиентов должно быть больше 0'
                )
        return ingredients

    @staticmethod
    def create_ingredients(recipe, ingredients):
        ingredient_list = []
        for ingredient_data in ingredients:
            ingredient_list.append(
                IngredientRecipe(
                    ingredient=ingredient_data.pop('id'),
                    amount=ingredient_data.pop('amount'),
                    recipe=recipe,
                )
            )
        IngredientRecipe.objects.bulk_create(ingredient_list)

    def create(self, validated_data):
        """Создаёт рецепт.
            Args:
               validated_data (dict): Данные для создания рецепта.
            Returns:
               Recipe: Созданый рецепт.
        """
        request = self.context.get('request', None)
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)

        self.create_ingredients(recipe, ingredients)

        return recipe

    def update(self, recipe, validated_data):
        """Обновляет рецепт.
            Args:
                recipe (Recipe): Рецепт для изменения.
                validated_data (dict): Изменённые данные.
            Returns:
                Recipe: Обновлённый рецепт.
        """
        recipe.tags.clear()
        IngredientRecipe.objects.filter(recipe=recipe).delete()
        recipe.tags.set(validated_data.pop('tags'))
        ingredients = validated_data.pop('ingredients')
        self.create_ingredients(recipe, ingredients)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context={
            'request': self.context.get('request')
        }).data


class RecipeShortSerializer(serializers.ModelSerializer):
    """ Сериализатор для избранных рецептов и покупок """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(CustomUserSerializer):
    """
        Сериализатор вывода авторов на которых подписан текущий пользователь.
    """
    recipes = RecipeShortSerializer(many=True, read_only=True)
    recipes_count = SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def get_recipes_count(self, obj):
        """ Показывает общее количество рецептов у каждого автора.
        Args:
            obj (User): Запрошенный пользователь.
        Returns:
            int: Количество рецептов созданных запрошенным пользователем.
        """
        return obj.recipes.count()


class CartSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок """

    class Meta:
        model = Cart
        fields = ('user', 'recipe',)

    def validate(self, data):
        user = data['user']
        if user.carts.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в корзину'
            )
        return data

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
