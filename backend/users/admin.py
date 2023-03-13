from django.contrib.admin import ModelAdmin, register, site
from users.models import CustomUser, Follow

site.site_header = 'Администрирование сайта Foodgram'


@register(CustomUser)
class UserAdmin(ModelAdmin):
    list_display = ('username', 'email',)
    list_filter = ('username', 'email',)
    search_fields = ('username', 'email',)


@register(Follow)
class FollowAdmin(ModelAdmin):
    list_display = ('user', 'author',)
    search_fields = ('user__username', 'author__username',)
