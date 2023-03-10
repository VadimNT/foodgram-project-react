from django.contrib.admin import site, ModelAdmin, register, display
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from core.texts import EMPTY_MSG
from recipes.models import Tag, Ingredient, Recipe, Favorite, Cart

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
    list_display = (
        'get_tags', 'get_author', 'name', 'image', 'text', 'cooking_time',
        'get_ingredients', 'get_favorite_count', 'get_image',
    )
    list_filter = ('name', 'author__username', 'tags__name',)
    search_fields = (
        'tags', 'author', 'name', 'image', 'text', 'cooking_time',
    )
    empty_value_display = EMPTY_MSG

    @display(description='Электронная почта автора')
    def get_author(self, obj):
        return obj.author.email

    @display(description='Картинка рецепта')
    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="80" hieght="30"')

    @display(description='Тэги')
    def get_tags(self, obj):
        list_ = [_.name for _ in obj.tags.all()]
        return ', '.join(list_)

    @display(description=' Ингредиенты ')
    def get_ingredients(self, obj):
        return '\n '.join([
            f'{item["ingredient__name"]} - {item["amount"]}'
            f' {item["ingredient__measurement_unit"]}.'
            for item in obj.recipe.values(
                'ingredient__name',
                'amount', 'ingredient__measurement_unit')])

    @display(description='В избранном')
    def get_favorite_count(self, obj):
        return obj.favorite_recipe.count()


@register(Cart)
class CartAdmin(ModelAdmin):
    list_display = ('user', 'recipe',)
    search_fields = ('user__username', 'recipe__name',)


@register(Favorite)
class FavoriteAdmin(ModelAdmin):
    list_display = ('user', 'recipe',)
    search_fields = ('user__username', 'recipe__name',)
