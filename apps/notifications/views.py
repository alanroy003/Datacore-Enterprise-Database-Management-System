# file: apps/notifications/views.py
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from .models import Notification
from .serializers import NotificationSerializer
from apps.core.utils import success_response


@extend_schema(tags=['notifications'])
class NotificationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    serializer_class  = NotificationSerializer
    http_method_names = ['get', 'patch', 'post', 'head', 'options']

    def get_queryset(self):
        return Notification.objects.filter(employee=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        n = self.get_object()
        n.mark_as_read()
        return Response(success_response(NotificationSerializer(n).data, 'Marked as read'))

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        count = self.get_queryset().filter(is_read=False).update(is_read=True, read_at=timezone.now())
        return Response(success_response({'marked': count}))

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        return Response(success_response({'count': self.get_queryset().filter(is_read=False).count()}))