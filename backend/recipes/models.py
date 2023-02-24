from django.db import models
from django.db.models import SET_NULL

from backend.users.models import Users


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=250,
    )
    color = models.CharField(
        verbose_name='Цветовой HEX-код',
        max_length=250,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Слаг тэга',
        max_length=250,
        unique=True
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self) -> str:
        return f'{self.name} (цвет: {self.color})'


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=250
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=250
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('name',)

    def __str__(self) -> str:
        return f'{self.name} {self.measurement_unit}'


class Recipe(models.Model):
    tags = models.ManyToManyField(
        verbose_name='Тэг',
        related_name='recipes',
        to=Tag
    )
    author = models.ForeignKey(
        verbose_name='Автор рецепта',
        related_name='recipes',
        to=Users,
        on_delete=SET_NULL,
        null=True,
    )
    ingredients = models.ManyToManyField(
        verbose_name='Ингридиенты',
        related_name='recipes',
        to=Ingredient,
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=250,
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='images/',
    )
    text = models.TextField(
        verbose_name='Описание',
        max_length=250,
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        default=0,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name}. Автор: {self.author.username}'
