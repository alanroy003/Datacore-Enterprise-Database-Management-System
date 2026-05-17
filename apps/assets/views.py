# file: apps/assets/views.py
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from drf_spectacular.utils import extend_schema

from .models import Asset, AssetLog, AssetExpiry
from .serializers import (
    AssetSerializer, AssetLogSerializer, AssetExpirySerializer,
    AssetCheckoutSerializer, AssetReturnSerializer,
)
from .filters import AssetFilter
from apps.accounts.permissions import IsAdminOrAbove, IsManagerOrAbove
from apps.accounts.models import Employee
from apps.core.utils import success_response, error_response


@extend_schema(tags=['assets'])
class AssetViewSet(ModelViewSet):
    serializer_class = AssetSerializer
    filterset_class  = AssetFilter
    search_fields    = ['name', 'serial_no']
    ordering_fields  = ['name', 'status', 'created_at']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrAbove()]
        if self.action in ['checkout', 'return_asset']:
            return [IsManagerOrAbove()]
        return [IsAuthenticated()]

    def get_queryset(self):
        u  = self.request.user
        qs = Asset.objects.prefetch_related('logs', 'expiries')
        return qs.all() if u.is_superadmin else qs.filter(company=u.company)

    def perform_create(self, serializer):
        if self.request.user.is_superadmin:
            serializer.save()
        else:
            serializer.save(company=self.request.user.company)

    @extend_schema(summary="Checkout asset to an employee")
    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        asset = self.get_object()
        if asset.status != 'available':
            return Response(error_response(f"Asset is '{asset.status}', cannot checkout."), status=400)
        s = AssetCheckoutSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        try:
            emp = Employee.objects.get(
                id=s.validated_data['employee_id'],
                company=request.user.company,
                is_active=True
            )
        except Employee.DoesNotExist:
            return Response(error_response('Employee not found in your company.'), status=404)
        AssetLog.objects.create(
            asset=asset, employee=emp,
            expected_return_date=s.validated_data.get('expected_return_date')
        )
        asset.status = 'assigned'
        asset.save()
        return Response(success_response(AssetSerializer(asset).data, 'Checked out successfully'))

    @extend_schema(summary="Return an assigned asset")
    @action(detail=True, methods=['post'])
    def return_asset(self, request, pk=None):
        asset = self.get_object()
        log   = asset.logs.filter(returned_at__isnull=True).first()
        if not log:
            return Response(error_response('Asset is not currently assigned.'), status=400)
        s = AssetReturnSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        log.returned_at         = timezone.now()
        log.condition_on_return = s.validated_data['condition_on_return']
        log.notes               = s.validated_data.get('notes', '')
        log.save()
        asset.condition = s.validated_data['condition_on_return']
        asset.status    = 'available'
        asset.save()
        return Response(success_response(AssetSerializer(asset).data, 'Returned successfully'))

    @extend_schema(summary="Full checkout history for this asset")
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        logs = self.get_object().logs.select_related('employee').all()
        return Response(success_response(AssetLogSerializer(logs, many=True).data))

    @extend_schema(summary="Current holder of this asset")
    @action(detail=True, methods=['get'])
    def current_holder(self, request, pk=None):
        log = self.get_object().logs.filter(returned_at__isnull=True).select_related('employee').first()
        return Response(success_response(AssetLogSerializer(log).data if log else None))


@extend_schema(tags=['asset-logs'])
class AssetLogViewSet(ReadOnlyModelViewSet):
    serializer_class = AssetLogSerializer

    def get_queryset(self):
        u  = self.request.user
        qs = AssetLog.objects.select_related('asset', 'employee')
        return qs.all() if u.is_superadmin else qs.filter(asset__company=u.company)


@extend_schema(tags=['asset-expiries'])
class AssetExpiryViewSet(ModelViewSet):
    serializer_class   = AssetExpirySerializer
    permission_classes = [IsAdminOrAbove]

    def get_queryset(self):
        u  = self.request.user
        qs = AssetExpiry.objects.select_related('asset')
        return qs.all() if u.is_superadmin else qs.filter(asset__company=u.company)