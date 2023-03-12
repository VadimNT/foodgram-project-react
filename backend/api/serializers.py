from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.validators import UniqueValidator

from recipes.models import Tag, Ingredient, Recipe, Cart, Favorite
from users.models import CustomUser, Follow


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = SerializerMethodField()

    username = serializers.RegexField(
        regex=r'^[\w.@+-]',
        validators=[
            UniqueValidator(queryset=CustomUser.objects.all())
        ],
        required=True,
    )
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(queryset=CustomUser.objects.all())
        ]
    )

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password',
        )

    def get_is_subscribed(self, obj):
        """
        Првоеряем подписку на пользователя
            :param obj: пользователь, который подписан
            :return: вернет True or False, если подписан
        """
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()

    def create(self, validated_data):
        """
            Создаёт нового пользователя с запрошенными полями.
            Args:
                validated_data (dict): Полученные проверенные данные.
            Returns:
                User: Созданный пользователь.
        """
        user = CustomUser(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                'Пользователь с таким именем уже существует!')
        return value


class ShortRecipeSerializer(serializers.ModelSerializer):
    """
        Сериализатор для модели Recipe.
        Определён укороченный набор полей для некоторых эндпоинтов.
    """

    class Meta:
        model = Recipe
        fields = 'id', 'name', 'image', 'cooking_time'
        read_only_fields = '__all__',


class SubscribeSerializer(UserSerializer):
    """
        Сериализатор вывода авторов на которых подписан текущий пользователь.
    """
    recipes = ShortRecipeSerializer()
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

    def get_is_subscribed(*args):
        """
            Всегда возвращаем True.
            Returns:
                bool: True
        """
        return True

    def get_recipes_count(self, obj):
        """ Показывает общее количество рецептов у каждого автора.
        Args:
            obj (User): Запрошенный пользователь.
        Returns:
            int: Количество рецептов созданных запрошенным пользователем.
        """
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[: int(limit)]
        serializer = RecipeSerializer(recipes, many=True, read_only=True)
        return serializer.data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """
        Сериализатор для вывода ингридиентов.
    """

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

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
        read_only_fields = (
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_is_favorited(self, recipe):
        """Проверка - находится ли рецепт в избранном.
            Args:
                recipe (Recipe): Переданный для проверки рецепт.
            Returns:
                bool: True - если рецепт в `избранном`
                у запращивающего пользователя, иначе - False.
        """
        user = self.context.get('view').request.user

        if user.is_aninymous:
            return False
        return user.favorited.filter(recipa=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        """Проверка - находится ли рецепт в списке  покупок.
            Args:
                recipe (Recipe): Переданный для проверки рецепт.
            Returns:
                bool: True - если рецепт в `списке покупок`
            у запращивающего пользователя, иначе - False.
        """
        user = self.context.get('view').request.user

        if user.is_anonymous:
            return False
        return user.carts.filter(recipe=recipe).exists()

    def create(self, validated_data):
        """Создаёт рецепт.
            Args:
               validated_data (dict): Данные для создания рецепта.
            Returns:
               Recipe: Созданый рецепт.
        """
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        # TODD расчет количества ингридентов
        return recipe

    def update(self, instance, validated_data):
        """Обновляет рецепт.
            Args:
                recipe (Recipe): Рецепт для изменения.
                validated_data (dict): Изменённые данные.
            Returns:
                Recipe: Обновлённый рецепт.
        """
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')


class RecipeShortSerializer(serializers.ModelSerializer):
    """ Сериализатор для избранных рецептов и покупок """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class CartSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок """

    class Meta:
        model = Cart
        fields = ('user', 'recipe',)

    def validate(self, data):
        user = data['user']
        if user.shopping_list.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в корзину'
            )
        return data

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    """  Сериализатор избранных рецептов """

    class Meta:
        model = Favorite
        fields = ('user', 'recipe',)

    def validate(self, data):
        user = data['user']
        if user.favorites.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное.'
            )
        return data

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
