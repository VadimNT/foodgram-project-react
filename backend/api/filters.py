from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(SearchFilter):
    search_param = 'name'

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.NumberFilter(method='filter')
    is_in_shopping_cart = filters.NumberFilter(
        method='filter'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart',)

    def filter(self, queryset, name, value):
        if (
                value
                and self.request.query_params.get("is_favorited")
        ):
            return queryset.filter(favorited__user=self.request.user)
        elif (
                value
                and self.request.query_params.get("is_in_shopping_cart")
        ):
            return queryset.filter(carts__user=self.request.user)
        return queryset
