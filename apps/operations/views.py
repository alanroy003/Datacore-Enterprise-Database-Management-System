# file: apps/operations/views.py
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from drf_spectacular.utils import extend_schema

from .models import AssetTransfer, Maintenance, MaintenanceStatus
from .serializers import AssetTransferSerializer, MaintenanceSerializer
from .services import TransferService
from apps.accounts.permissions import IsAdminOrAbove, IsManagerOrAbove
from apps.assets.models import Asset
from apps.core.utils import success_response, error_response


@extend_schema(tags=['transfers'])
class AssetTransferViewSet(ModelViewSet):
    serializer_class  = AssetTransferSerializer
    http_method_names = ['get', 'post', 'head', 'options']  # transfers are immutable

    def get_permissions(self):
        return [IsManagerOrAbove()] if self.action == 'create' else [IsAuthenticated()]

    def get_queryset(self):
        u  = self.request.user
        qs = AssetTransfer.objects.select_related('asset', 'from_employee', 'to_employee')
        return qs.all() if u.is_superadmin else qs.filter(asset__company=u.company)

    def create(self, request, *args, **kwargs):
        s = AssetTransferSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        try:
            asset = Asset.objects.get(id=d['asset'].id, company=request.user.company)
            transfer = TransferService.execute(
                asset=asset, from_employee=d['from_employee'],
                to_employee=d['to_employee'], reason=d.get('reason', ''),
                created_by=request.user,
            )
        except (Asset.DoesNotExist, ValueError) as e:
            return Response(error_response(str(e)), status=400)
        return Response(
            success_response(AssetTransferSerializer(transfer).data, 'Transferred'),
            status=201
        )


@extend_schema(tags=['maintenance'])
class MaintenanceViewSet(ModelViewSet):
    serializer_class = MaintenanceSerializer

    def get_permissions(self):
        if self.action in ['create', 'destroy']:               return [IsAdminOrAbove()]
        if self.action in ['mark_in_progress', 'complete']:    return [IsManagerOrAbove()]
        return [IsAuthenticated()]

    def get_queryset(self):
        u  = self.request.user
        qs = Maintenance.objects.select_related('asset', 'created_by')
        return qs.all() if u.is_superadmin else qs.filter(asset__company=u.company)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @extend_schema(summary="Mark maintenance as in progress")
    @action(detail=True, methods=['post'])
    def mark_in_progress(self, request, pk=None):
        m = self.get_object()
        m.status = MaintenanceStatus.IN_PROGRESS
        m.save()
        m.asset.status = 'in_maintenance'
        m.asset.save()
        return Response(success_response(MaintenanceSerializer(m).data, 'In progress'))

    @extend_schema(summary="Complete maintenance")
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        m = self.get_object()
        m.status         = MaintenanceStatus.COMPLETED
        m.completed_date = timezone.now().date()
        if 'cost' in request.data:
            m.cost = request.data['cost']
        m.save()
        m.asset.status = 'available'
        m.asset.save()
        return Response(success_response(MaintenanceSerializer(m).data, 'Completed'))