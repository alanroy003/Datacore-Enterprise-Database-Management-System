# file: apps/notifications/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone


class NotificationType(models.TextChoices):
    EXPIRY_ALERT     = 'expiry_alert',     'Expiry Alert'
    OVERDUE_RETURN   = 'overdue_return',   'Overdue Return'
    TRANSFER_REQUEST = 'transfer_request', 'Transfer'
    MAINTENANCE_DUE  = 'maintenance_due',  'Maintenance Due'
    SYSTEM           = 'system',           'System'


class Notification(models.Model):
    employee          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NotificationType.choices, default=NotificationType.SYSTEM)
    title             = models.CharField(max_length=255)
    message           = models.TextField()
    is_read           = models.BooleanField(default=False)
    read_at           = models.DateTimeField(null=True, blank=True)
    created_at        = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()