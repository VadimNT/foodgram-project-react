from django.contrib.admin import ModelAdmin, register, site

from backend.users.models import Cart, Favorite, Follow, User

site.site_header = 'Администрирование сайта Foodgram'


@register(User)
class UserAdmin(ModelAdmin):
    list_display = ('username', 'email',)
    list_filter = ('username', 'email',)
    search_fields = ('username', 'email',)


@register(Cart)
class CartAdmin(ModelAdmin):
    list_display = ('user', 'recipe',)
    search_fields = ('user__username', 'recipe__name',)


@register(Favorite)
class FavoriteAdmin(ModelAdmin):
    list_display = ('user', 'recipe',)
    search_fields = ('user__username', 'recipe__name',)


@register(Follow)
class FollowAdmin(ModelAdmin):
    list_display = ('user', 'author',)
    search_fields = ('user__username', 'author__username',)
