"""Модуль для создания, настройки и управления моделями пакета `recipe`.
Models:
    Recipe:
        Основная модель приложения, через которую описываются рецепты.
    Tag:
       Модель для группировки рецептов по тэгам.
       Связана с Recipe через Many-To-Many.
    Ingredient:
        Модель для описания ингредиентов.
        Связана с Recipe через модель AmountIngredient (Many-To-Many).
    AmountIngredient:
        Модель для связи Ingredient и Recipe.
        Также указывает количество ингридиента.
"""
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import SET_NULL, CASCADE

from core.enums import (MAX_LEN_RECIPES_CHARFIELD, MAX_LEN_CODE_COLOR,
                        MAX_LEN_MEASUREMENT, MIN_COOKING_TIME,
                        MAX_COOKING_TIME, MIN_AMOUNT_INGREDIENTS,
                        MAX_AMOUNT_INGREDIENTS, )

User = get_user_model()


class Tag(models.Model):
    """Тэги для рецептов.
        Связано с моделью Recipe через many-to-many.
        Поля `name` и 'slug` - обязательны для заполнения.
        Attributes:
            name(str):
                Название тэга. Установлены ограничения по длине и уникальности.
            color(str):
                Цвет тэга в HEX-кодировке. По умолчанию - чёрный
            slug(str):
                Те же правила, что и для атрибута `name`, но для корректной работы
                с фронтэндом следует заполнять латинскими буквами.
    """
    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LEN_RECIPES_CHARFIELD,
        unique=True,
    )
    color = models.CharField(
        verbose_name='Цветовой HEX-код',
        max_length=MAX_LEN_CODE_COLOR,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Слаг тэга',
        max_length=MAX_LEN_RECIPES_CHARFIELD,
        unique=True
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self) -> str:
        return f'{self.name} (цвет: {self.color})'


class Ingredient(models.Model):
    """Ингридиенты для рецепта.
        Связано с моделью Recipe через М2М (AmountIngredient).
        Attributes:
            name(str):
                Название ингридиента.
                Установлены ограничения по длине и уникальности.
            measurement_unit(str):
                Единицы измерения ингридентов (граммы, штуки, литры и т.п.).
                Установлены ограничения по длине.
    """
    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LEN_RECIPES_CHARFIELD
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=MAX_LEN_MEASUREMENT
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('name',)

    def __str__(self) -> str:
        return f'{self.name} {self.measurement_unit}'


class Recipe(models.Model):
    """Модель для рецептов.
    Основная модель приложения описывающая рецепты.
    Attributes:
        name(str):
           Название рецепта. Установлены ограничения по длине.
        author(int):
            Автор рецепта. Связан с моделю User через ForeignKey.
        in_favorites(int):
            Связь many-to-many с моделью User.
            Создаётся при добавлении пользователем рецепта в `избранное`.
        tags(int):
            Связь many-to-many с моделью Tag.
        ingredients(int):
            Связь many-to-many с моделью Ingredient. Связь создаётся посредством модели
            AmountIngredient с указанием количества ингридиента.
        in_carts(int):
            Связь many-to-many с моделью User.
            Создаётся при добавлении пользователем рецепта в `покупки`.
        image(str):
            Изображение рецепта. Указывает путь к изображению.
        text(str):
            Описание рецепта. Установлены ограничения по длине.
        cooking_time(int):
            Время приготовления рецепта.
            Установлены ограничения по максимальным и минимальным значениям.
    """
    tags = models.ManyToManyField(
        verbose_name='Тэг',
        related_name='recipes',
        to=Tag
    )
    author = models.ForeignKey(
        verbose_name='Автор рецепта',
        related_name='recipes',
        to=User,
        on_delete=SET_NULL,
        null=True,
    )
    ingredients = models.ManyToManyField(
        to=Ingredient,
        verbose_name='Ингридиенты',
        related_name='recipes',
        through='recipes.IngredientRecipe',
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LEN_RECIPES_CHARFIELD,
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='images/',
    )
    text = models.TextField(
        verbose_name='Описание',
        max_length=MAX_LEN_RECIPES_CHARFIELD,
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        default=0,
        validators=(
            MinValueValidator(
                MIN_COOKING_TIME,
                'Ваше блюдо приготовлено!',
            ),
            MaxValueValidator(
                MAX_COOKING_TIME,
                'Ваше блюдо слишком долго готовится!',
            ),
        ),
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name}. Автор: {self.author.username}'


class IngredientRecipe(models.Model):
    """Количество ингридиентов в блюде.
    Модель связывает Recipe и Ingredient с указанием количества ингридиента.
    Attributes:
        recipe(int):
            Связаный рецепт. Связь через ForeignKey.
        ingredients(int):
            Связаный ингридиент. Связь через ForeignKey.
        amount(int):
            Количиства ингридиента в рецепте. Установлены ограничения
            по минимальному и максимальному значениям.
    """
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='В каких рецептах',
        related_name='ingredient',
        on_delete=CASCADE,
    )
    ingredients = models.ForeignKey(
        Ingredient,
        verbose_name='Связанные ингредиенты',
        related_name='recipe',
        on_delete=CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        default=0,
        validators=(
            MinValueValidator(
                MIN_AMOUNT_INGREDIENTS,
                'Добавьте ингриденты.',
            ),
            MaxValueValidator(
                MAX_AMOUNT_INGREDIENTS,
                'Очень много ингридиентов!',
            ),
        ),
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингредиенты рецепта'

    def __str__(self) -> str:
        return f'{self.amount} {self.ingredients}'


class Favorite(models.Model):
    """Избранные рецепты.
    Модель связывает Recipe и  User.
    Attributes:
        recipe(int):
            Связаный рецепт. Связь через ForeignKey.
        user(int):
            Связаный пользователь. Связь через ForeignKey.
        date_added(datetime):
    """
    recipe = models.ForeignKey(
        verbose_name='Рецепт',
        related_name='favorited',
        to=Recipe,
        on_delete=CASCADE,
    )
    user = models.ForeignKey(
        verbose_name='Пользователь',
        related_name='favorited',
        to=User,
        on_delete=CASCADE,
    )

    class Meta:
        verbose_name = 'Избранный рецепт пользователя',
        verbose_name_plural = 'Избранные рецепты пользователя'

    def __str__(self) -> str:
        return f'{self.user} -> {self.recipe}'


class Cart(models.Model):
    """Рецепты в корзине покупок.
    Модель связывает Recipe и  User.
    Attributes:
        recipe(int):
            Связаный рецепт. Связь через ForeignKey.
        user(int):
            Связаный пользователь. Связь через ForeignKey.
    """
    user = models.ForeignKey(
        verbose_name='Пользователь',
        related_name='carts',
        to=User,
        on_delete=CASCADE,
    )
    recipe = models.ForeignKey(
        verbose_name='Рецепт',
        related_name='carts',
        to=Recipe,
        on_delete=CASCADE,
    )

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'

    def __str__(self) -> str:
        return f'{self.user} -> {self.recipe}'
