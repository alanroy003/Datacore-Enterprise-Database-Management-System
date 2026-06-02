# file: apps/core/models.py
from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    class ActionType(models.TextChoices):
        CREATE = 'create', 'Create'
        UPDATE = 'update', 'Update'
        DELETE = 'delete', 'Delete'

    action_type  = models.CharField(max_length=10, choices=ActionType.choices)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    target_table = models.CharField(max_length=100)
    target_id    = models.IntegerField()
    old_value    = models.JSONField(null=True, blank=True)
    new_value    = models.JSONField(null=True, blank=True)
    ip_address   = models.GenericIPAddressField(null=True, blank=True)
    timestamp    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']


class Report(models.Model):
    class ReportType(models.TextChoices):
        UTILIZATION = 'asset_utilization', 'Asset Utilization'
        EXPIRY      = 'expiry_summary',    'Expiry Summary'
        OVERDUE     = 'overdue',           'Overdue'

    generated_by  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='reports')
    report_type   = models.CharField(max_length=30, choices=ReportType.choices)
    generated_at  = models.DateTimeField(auto_now_add=True)
    data_snapshot = models.JSONField(null=True, blank=True)
    file_path     = models.CharField(max_length=512, blank=True)

    class Meta:
        ordering = ['-generated_at']


class SchedulerLog(models.Model):
    class RunStatus(models.TextChoices):
        SUCCESS = 'success', 'Success'
        FAILED  = 'failed',  'Failed'
        PARTIAL = 'partial', 'Partial'

    job_name          = models.CharField(max_length=100)
    ran_at            = models.DateTimeField(auto_now_add=True)
    status            = models.CharField(max_length=10, choices=RunStatus.choices)
    records_processed = models.IntegerField(default=0)
    error_message     = models.TextField(blank=True)

    class Meta:
        ordering = ['-ran_at']