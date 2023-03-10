from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


class CustomUser(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)

    email = models.EmailField(
        'Email',
        max_length=200,
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=150
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150
    )
    username = models.CharField(
        'username',
        max_length=254,
        unique=True,
        validators=(UnicodeUsernameValidator(),)
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('last_name',)

    def __str__(self):
        return self.email


class Follow(models.Model):
    """Подписки пользователей друг на друга.
    Attributes:
    author(int):
        Автор рецепта. Связь через ForeignKey.
    user(int):
        Подписчик Связь через ForeignKey.
    """
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        CustomUser,
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
