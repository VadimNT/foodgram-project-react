from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response


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
            instance, created = target_subscribe.objects.get_or_create(
                user=request.user, recipe=obj
            )
            if not created:
                return Response(
                    {"errors": "Ошибка подписки"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = type_serializer(obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            target_subscribe.objects.filter(
                user=request.user,
                recipe=obj
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)
