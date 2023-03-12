from recipes.models import IngredientRecipe


def set_ingredient_in_recipe(recipe, ingredients):
    for ingredient in ingredients:
        IngredientRecipe.objects.get_or_create(
            recipe=recipe,
            ingredients=ingredient['ingredient'],
            amount=ingredient['amount']
        )
