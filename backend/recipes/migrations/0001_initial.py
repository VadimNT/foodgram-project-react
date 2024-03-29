# Generated by Django 3.2.16 on 2023-03-16 08:26

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Рецепт в списке покупок',
                'verbose_name_plural': 'Рецепты в списке покупок',
                'ordering': ('-id',),
            },
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': ('Избранный рецепт пользователя',),
                'verbose_name_plural': 'Избранные рецепты пользователя',
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='Название')),
                ('measurement_unit', models.CharField(max_length=24, verbose_name='Единицы измерения')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингридиенты',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='IngredientRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(1, 'Добавьте ингриденты.'), django.core.validators.MaxValueValidator(32, 'Очень много ингридиентов!')], verbose_name='Количество')),
            ],
            options={
                'verbose_name': 'Ингридиент',
                'verbose_name_plural': 'Ингредиенты рецепта',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Название')),
                ('image', models.ImageField(upload_to='recipes/image/', verbose_name='Изображение')),
                ('text', models.TextField(max_length=5000, verbose_name='Описание')),
                ('cooking_time', models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(1, 'Ваше блюдо приготовлено!'), django.core.validators.MaxValueValidator(300, 'Ваше блюдо слишком долго готовится!')], verbose_name='Время приготовления')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
                'ordering': ('-id',),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True, verbose_name='Название')),
                ('color', models.CharField(max_length=7, unique=True, validators=[django.core.validators.RegexValidator(message='Проверьте HEX формат', regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')], verbose_name='Цветовой HEX-код')),
                ('slug', models.SlugField(max_length=64, unique=True, verbose_name='Слаг тэга')),
            ],
            options={
                'verbose_name': 'Тэг',
                'verbose_name_plural': 'Тэги',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='TagRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tag_recipes', to='recipes.recipe', verbose_name='Рецепт')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tag_recipes', to='recipes.tag', verbose_name='Тэги')),
            ],
            options={
                'verbose_name': 'Тэг рецепта',
                'verbose_name_plural': 'Тэги рецептов',
                'ordering': ('recipe__name', 'tag__name'),
            },
        ),
    ]
