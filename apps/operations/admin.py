# file: apps/operations/admin.py
from django.contrib import admin
from .models import AssetTransfer, Maintenance


@admin.register(AssetTransfer)
class AssetTransferAdmin(admin.ModelAdmin):
    list_display    = ['asset', 'from_employee', 'to_employee', 'transferred_at']
    readonly_fields = ['asset', 'from_employee', 'to_employee', 'transferred_at', 'created_by']
    def has_add_permission(self, request): return False


@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display    = ['asset', 'scheduled_date', 'status', 'cost']
    list_filter     = ['status']
    readonly_fields = ['created_at', 'updated_at', 'created_by']