# file: apps/notifications/admin.py
from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display    = ['employee', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter     = ['notification_type', 'is_read']
    search_fields   = ['employee__name', 'title']
    readonly_fields = ['created_at', 'read_at']