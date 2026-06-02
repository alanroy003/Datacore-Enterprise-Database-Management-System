# file: apps/core/views.py
import csv
from django.http import HttpResponse
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from .models import AuditLog, Report
from .serializers import AuditLogSerializer, ReportSerializer
from apps.accounts.permissions import IsAdminOrAbove
from apps.core.utils import success_response


@extend_schema(tags=['audit'])
class AuditLogViewSet(ReadOnlyModelViewSet):
    serializer_class   = AuditLogSerializer
    permission_classes = [IsAdminOrAbove]
    filterset_fields   = ['action_type', 'target_table', 'performed_by']
    search_fields      = ['target_table', 'performed_by__name']
    ordering_fields    = ['timestamp']

    def get_queryset(self):
        u  = self.request.user
        qs = AuditLog.objects.select_related('performed_by')
        return qs.all() if u.is_superadmin else qs.filter(performed_by__company=u.company)


@extend_schema(tags=['reports'])
class ReportViewSet(ModelViewSet):
    serializer_class   = ReportSerializer
    permission_classes = [IsAdminOrAbove]
    http_method_names  = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        u  = self.request.user
        qs = Report.objects.select_related('generated_by')
        return qs.all() if u.is_superadmin else qs.filter(generated_by__company=u.company)

    @action(detail=False, methods=['post'])
    def generate(self, request):
        from apps.core.tasks import generate_report_task
        task = generate_report_task.delay(
            request.data.get('report_type', 'asset_utilization'),
            request.user.id
        )
        return Response(success_response({'task_id': task.id}, 'Report queued'), status=202)

    @action(detail=True, methods=['get'])
    def export(self, request, pk=None):
        r    = self.get_object()
        resp = HttpResponse(content_type='text/csv')
        resp['Content-Disposition'] = f'attachment; filename="report_{r.id}.csv"'
        w = csv.writer(resp)
        d = r.data_snapshot
        if isinstance(d, list) and d:
            w.writerow(d[0].keys())
            for row in d: w.writerow(row.values())
        elif isinstance(d, dict):
            for k, v in d.items(): w.writerow([k, v])
        return resp