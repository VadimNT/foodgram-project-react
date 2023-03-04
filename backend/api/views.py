from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from backend.api.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from backend.api.serializers import TagSerializer, IngredientSerializer, \
    UserSerializer
from backend.recipes.models import Tag, Ingredient


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
    serializer_class = UserSerializer


class IngredientViewSet(ModelViewSet):
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    queryset = Ingredient.objects.all()


class RecipeViewSet(ModelViewSet):
    pass
