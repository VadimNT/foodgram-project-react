from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F, Q

from foodgram.settings import MAX_LEN_EMAIL_FIELD, MAX_LEN_USERS_FIELD


class CustomUser(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)

    email = models.EmailField(
        'Email',
        max_length=MAX_LEN_EMAIL_FIELD,
        unique=True,
    )
    password = models.CharField(
        'password',
        max_length=MAX_LEN_USERS_FIELD
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
            ),
            models.CheckConstraint(
                check=~Q(user=F('author')),
                name='no_self_follow'
            )
        ]

    def __str__(self) -> str:
        return f'{self.user.username} -> {self.author.username}'
