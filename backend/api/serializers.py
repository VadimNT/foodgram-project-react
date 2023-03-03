from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.validators import UniqueValidator

from backend.recipes.models import Tag
from backend.users.models import User, Follow


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = SerializerMethodField()

    username = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ],
        required=True,
    )
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ]
    )

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_aninymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = '__all__',


class RecipeSerializer(serializers.ModelSerializer):
    pass


class IngredientSerializer(serializers.ModelSerializer):
    pass
