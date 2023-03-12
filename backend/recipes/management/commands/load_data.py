import json

from django.core.management.base import BaseCommand

from foodgram import settings
from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = ' Загрузить данные в модель ингредиентов '

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Старт команды'))
        data_path = settings.BASE_DIR
        with open(
                f'{data_path}/data/ingredients.json',
                encoding='utf-8',
        ) as data_file_ingredients:
            ingredient_data = json.loads(data_file_ingredients.read())
            for ingredients in ingredient_data:
                Ingredient.objects.get_or_create(**ingredients)

        self.stdout.write(self.style.SUCCESS('Данные загружены'))
