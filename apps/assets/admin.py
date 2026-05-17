# file: apps/assets/admin.py
from django.contrib import admin
from .models import Asset, AssetLog, AssetExpiry


class ExpiryInline(admin.TabularInline):
    model  = AssetExpiry
    extra  = 0
    fields = ['expiry_type', 'expiry_date', 'days_before_alert', 'alert_sent']
    readonly_fields = ['alert_sent']


class LogInline(admin.TabularInline):
    model  = AssetLog
    extra  = 0
    readonly_fields = ['employee', 'checked_out_at', 'returned_at']
    can_delete = False


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display    = ['name', 'asset_type', 'company', 'status', 'condition', 'warranty_expiry']
    list_filter     = ['status', 'condition', 'asset_type', 'company']
    search_fields   = ['name', 'serial_no']
    readonly_fields = ['created_at', 'updated_at']
    inlines         = [ExpiryInline, LogInline]
    actions         = ['retire']

    @admin.action(description='Mark selected as retired')
    def retire(self, request, qs):
        qs.update(status='retired')


@admin.register(AssetLog)
class AssetLogAdmin(admin.ModelAdmin):
    list_display    = ['asset', 'employee', 'checked_out_at', 'returned_at']
    list_filter     = ['returned_at']
    search_fields   = ['asset__name', 'employee__name']
    readonly_fields = ['checked_out_at']