# file: apps/operations/services.py
from django.db import transaction
from django.utils import timezone
from apps.assets.models import AssetLog


class TransferService:
    @staticmethod
    @transaction.atomic
    def execute(asset, from_employee, to_employee, reason, created_by):
        from .models import AssetTransfer
        from apps.notifications.services import NotificationService

        if asset.status != 'assigned':
            raise ValueError(f"'{asset.name}' is not currently assigned.")

        log = asset.logs.filter(returned_at__isnull=True).first()
        if not log or log.employee_id != from_employee.id:
            raise ValueError(f"'{asset.name}' is not assigned to {from_employee.name}.")

        if from_employee.id == to_employee.id:
            raise ValueError('Cannot transfer to the same employee.')

        # Close old log
        log.returned_at         = timezone.now()
        log.condition_on_return = asset.condition
        log.save()

        # Open new log
        AssetLog.objects.create(asset=asset, employee=to_employee)

        # Record transfer
        transfer = AssetTransfer.objects.create(
            asset=asset, from_employee=from_employee,
            to_employee=to_employee, reason=reason, created_by=created_by,
        )

        # Notify both employees
        NotificationService.create(
            from_employee, 'transfer_request',
            'Asset transferred away',
            f"'{asset.name}' has been transferred to {to_employee.name}."
        )
        NotificationService.create(
            to_employee, 'transfer_request',
            'Asset transferred to you',
            f"'{asset.name}' has been transferred to you from {from_employee.name}."
        )

        return transfer