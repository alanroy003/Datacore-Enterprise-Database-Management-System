# file: apps/operations/models.py
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class AssetTransfer(models.Model):
    asset         = models.ForeignKey('assets.Asset', on_delete=models.CASCADE, related_name='transfers')
    from_employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transfers_out')
    to_employee   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transfers_in')
    reason        = models.TextField(blank=True)
    created_by    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='transfers_initiated')
    transferred_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-transferred_at']

    def __str__(self):
        return f"{self.asset.name}: {self.from_employee.name} → {self.to_employee.name}"

    def clean(self):
        if self.from_employee_id == self.to_employee_id:
            raise ValidationError('Cannot transfer to the same employee.')


class MaintenanceStatus(models.TextChoices):
    PENDING     = 'pending',     'Pending'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED   = 'completed',   'Completed'
    SKIPPED     = 'skipped',     'Skipped'


class Maintenance(models.Model):
    asset          = models.ForeignKey('assets.Asset', on_delete=models.CASCADE, related_name='maintenance_records')
    scheduled_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    status         = models.CharField(max_length=20, choices=MaintenanceStatus.choices, default=MaintenanceStatus.PENDING)
    vendor         = models.CharField(max_length=255, blank=True)
    cost           = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes          = models.TextField(blank=True)
    created_by     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='maintenance_created')
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_date']

    def clean(self):
        if self.completed_date and self.completed_date < self.scheduled_date:
            raise ValidationError('Completed date cannot be before scheduled date.')