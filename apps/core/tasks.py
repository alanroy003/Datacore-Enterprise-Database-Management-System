# file: apps/core/tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .utils import log_scheduler_run


@shared_task(name='apps.core.tasks.check_expiry_alerts')
def check_expiry_alerts():
    from apps.assets.models import AssetExpiry
    from apps.notifications.services import NotificationService
    try:
        threshold = timezone.now().date() + timedelta(days=30)
        expiries  = AssetExpiry.objects.filter(alert_sent=False, expiry_date__lte=threshold).select_related('asset')
        count = 0
        for e in expiries:
            holder = e.asset.current_holder
            if holder:
                days = (e.expiry_date - timezone.now().date()).days
                NotificationService.create(holder.employee, 'expiry_alert', f"Expiry in {days} days", f"'{e.asset.name}' {e.expiry_type} expires {e.expiry_date}.")
                e.alert_sent = True
                e.save()
                count += 1
        log_scheduler_run('check_expiry_alerts', 'success', count)
    except Exception as ex:
        log_scheduler_run('check_expiry_alerts', 'failed', 0, str(ex))
        raise


@shared_task(name='apps.core.tasks.flag_overdue_returns')
def flag_overdue_returns():
    from apps.assets.models import AssetLog
    from apps.notifications.services import NotificationService
    try:
        today = timezone.now().date()
        logs  = AssetLog.objects.filter(returned_at__isnull=True, expected_return_date__lt=today).select_related('asset', 'employee')
        count = 0
        for log in logs:
            NotificationService.create(log.employee, 'overdue_return', 'Overdue asset return', f"'{log.asset.name}' was due {log.expected_return_date}.")
            count += 1
        log_scheduler_run('flag_overdue_returns', 'success', count)
    except Exception as ex:
        log_scheduler_run('flag_overdue_returns', 'failed', 0, str(ex))
        raise


@shared_task(name='apps.core.tasks.notify_upcoming_maintenance')
def notify_upcoming_maintenance():
    from apps.operations.models import Maintenance, MaintenanceStatus
    from apps.notifications.services import NotificationService
    try:
        threshold = timezone.now().date() + timedelta(days=7)
        items     = Maintenance.objects.filter(status=MaintenanceStatus.PENDING, scheduled_date__lte=threshold).select_related('asset')
        count = 0
        for m in items:
            holder = m.asset.current_holder
            if holder:
                NotificationService.create(holder.employee, 'maintenance_due', 'Maintenance due soon', f"'{m.asset.name}' scheduled {m.scheduled_date}.")
                count += 1
        log_scheduler_run('notify_upcoming_maintenance', 'success', count)
    except Exception as ex:
        log_scheduler_run('notify_upcoming_maintenance', 'failed', 0, str(ex))
        raise


@shared_task(name='apps.core.tasks.generate_weekly_report')
def generate_weekly_report():
    from apps.companies.models import Company
    from apps.assets.models import Asset, AssetLog
    from .models import Report
    try:
        count = 0
        for co in Company.objects.all():
            assets   = Asset.objects.filter(company=co)
            snapshot = {
                'company':   co.name,
                'total':     assets.count(),
                'by_status': {s: assets.filter(status=s).count() for s in ['available', 'assigned', 'in_maintenance', 'retired']},
                'overdue':   AssetLog.objects.filter(asset__company=co, returned_at__isnull=True, expected_return_date__lt=timezone.now().date()).count(),
            }
            Report.objects.create(report_type='asset_utilization', data_snapshot=snapshot)
            count += 1
        log_scheduler_run('generate_weekly_report', 'success', count)
    except Exception as ex:
        log_scheduler_run('generate_weekly_report', 'failed', 0, str(ex))
        raise


@shared_task(name='apps.core.tasks.generate_report_task')
def generate_report_task(report_type, user_id):
    from apps.accounts.models import Employee
    from apps.assets.models import Asset
    from .models import Report
    user = Employee.objects.get(id=user_id)
    data = list(Asset.objects.filter(company=user.company).values('id', 'name', 'asset_type', 'status', 'condition'))
    Report.objects.create(generated_by=user, report_type=report_type, data_snapshot=data)