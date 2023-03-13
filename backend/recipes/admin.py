from django.contrib.admin import display, ModelAdmin, register, site
from django.utils.html import format_html
from core.texts import EMPTY_MSG
from recipes.models import Cart, Favorite, Ingredient, Recipe, Tag

site.site_header = 'Администрирование сайта Foodgram'


@register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ('name', 'slug', 'color_code',)
    search_fields = ('name', 'color',)

    empty_value_display = EMPTY_MSG

    @display(description='Colored')
    def color_code(self, obj: Tag):
        return format_html(
            '<span style="color: #{};">{}</span>',
            obj.color[1:], obj.color
        )

    color_code.short_description = 'Цветовой код тэга'


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = EMPTY_MSG


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ('author', 'name', 'cooking_time',
                    'get_favorites', 'get_ingredients',)
    search_fields = ('name', 'author', 'tags')
    list_filter = ('author', 'name', 'tags')
    empty_value_display = EMPTY_MSG

    def get_favorites(self, obj):
        return obj.favorited.count()

    get_favorites.short_description = 'Избранное'

    def get_ingredients(self, obj):
        return ', '.join([
            ingredients.name for ingredients
            in obj.ingredients.all()])

    get_ingredients.short_description = 'Ингридиенты'


@register(Cart)
class CartAdmin(ModelAdmin):
    list_display = ('user', 'recipe',)
    search_fields = ('user__username', 'recipe__name',)


@register(Favorite)
class FavoriteAdmin(ModelAdmin):
    list_display = ('user', 'recipe',)
    search_fields = ('user__username', 'recipe__name',)
