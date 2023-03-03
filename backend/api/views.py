from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from backend.api.permissions import IsAdminOrReadOnly
from backend.api.serializers import TagSerializer
from backend.recipes.models import Tag


# Create your views here.
class TagViewSet(ModelViewSet):
    """Работает с тэгами.
       Изменение и создание тэгов разрешено только админам,
       остальным только разрешен просмотр
       """
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Tag.objects.all()


class UserViewSet(ModelViewSet):
    pass


class IngredientViewSet(ModelViewSet):
    pass


class RecipeViewSet(ModelViewSet):
    pass
