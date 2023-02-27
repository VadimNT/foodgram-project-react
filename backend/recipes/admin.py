from django.contrib.admin import site, ModelAdmin, register

from backend.recipes.models import Tag, Ingredient, Recipe

site.site_header = 'Администрирование сайта Foodgram'


@register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'slug')


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name')
    search_fields = ('name', 'measurement_unit')


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ('tags', 'author', 'name', 'image', 'text', 'cooking_time')
    list_filter = ('name', 'author__username', 'tags__name')
    search_fields = ('tags', 'author', 'name', 'image', 'text', 'cooking_time')
    # TODO На странице рецепта вывести общее число добавлений этого рецепта
    #  в избранное.
