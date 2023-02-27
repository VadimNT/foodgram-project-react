from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import CASCADE, SET_NULL

from backend.recipes.models import Recipe

User = get_user_model()


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
        related_name='recipes',
        to=Recipe,
        on_delete=CASCADE,
    )
    user = models.ForeignKey(
        verbose_name='Пользователь',
        related_name='users',
        to=User,
        on_delete=CASCADE,
    )

    class Meta:
        verbose_name = 'Избранный рецепт пользователя',
        verbose_name_plural = 'Избранные рецепты пользователя'

    def __str__(self) -> str:
        return f'{self.user} -> {self.recipe}'


class Follow(models.Model):
    """Подписки пользователей друг на друга.
    Attributes:
    author(int):
        Автор рецепта. Связь через ForeignKey.
    user(int):
        Подписчик Связь через ForeignKey.
    date_added(datetime):
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follwer',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписка автора',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['user']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow'
            )
        ]

    def __str__(self) -> str:
        return f'{self.user.username} -> {self.author.username}'


class Cart(models.Model):
    """Рецепты в корзине покупок.
    Модель связывает Recipe и  User.
    Attributes:
        recipe(int):
            Связаный рецепт. Связь через ForeignKey.
        user(int):
            Связаный пользователь. Связь через ForeignKey.
        date_added(datetime):
            Дата добавления рецепта в корзину.
    """
    user = models.ForeignKey(
        verbose_name='Пользователь',
        related_name='users',
        to=User,
        on_delete=CASCADE,
    )
    recipe = models.ManyToManyField(
        verbose_name='Рецепт',
        related_name='recipe',
        to=Recipe,
        on_delete=SET_NULL,
    )

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'

    def __str__(self) -> str:
        return f'{self.user} -> {self.recipe}'
