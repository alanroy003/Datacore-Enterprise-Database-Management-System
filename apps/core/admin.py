# file: apps/core/admin.py
from django.contrib import admin
from .models import AuditLog, Report, SchedulerLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display    = ['action_type', 'performed_by', 'target_table', 'target_id', 'timestamp']
    list_filter     = ['action_type', 'target_table']
    search_fields   = ['performed_by__name', 'target_table']
    readonly_fields = ['action_type', 'performed_by', 'target_table', 'target_id', 'old_value', 'new_value', 'ip_address', 'timestamp']
    def has_add_permission(self, r):            return False
    def has_change_permission(self, r, o=None): return False
    def has_delete_permission(self, r, o=None): return False


@admin.register(SchedulerLog)
class SchedulerLogAdmin(admin.ModelAdmin):
    list_display    = ['job_name', 'status', 'records_processed', 'ran_at']
    list_filter     = ['status', 'job_name']
    readonly_fields = ['job_name', 'ran_at', 'status', 'records_processed', 'error_message']
    def has_add_permission(self, r):            return False
    def has_change_permission(self, r, o=None): return False