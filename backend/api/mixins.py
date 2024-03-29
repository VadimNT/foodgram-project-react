from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Favorite


class SubscribeStatusViewSetMixin:
    def _set_status_favorite(
            self,
            request,
            target_model,
            target_subscribe,
            type_serializer
    ):
        obj = get_object_or_404(
            target_model,
            pk=self.kwargs[self.lookup_field]
        )
        if request.method == "POST":
            if target_subscribe == Favorite:
                instance, created = target_subscribe.objects.get_or_create(
                    user=request.user, recipe=obj
                )
                serializer = type_serializer(obj)
            else:
                instance, created = target_subscribe.objects.get_or_create(
                    user=request.user, author=obj
                )
                serializer = type_serializer(obj, data=request.data,
                                             context={'request': request})
                serializer.is_valid(raise_exception=True)
            if not created:
                return Response(
                    {"errors": "Ошибка подписки"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            if target_subscribe == Favorite:
                target_subscribe.objects.filter(
                    user=request.user,
                    recipe=obj
                ).delete()
            else:
                target_subscribe.objects.filter(
                    user=request.user,
                    author=obj
                ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)
