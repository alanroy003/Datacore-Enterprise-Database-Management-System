# file: config/celery.py
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

app = Celery('dataops')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check-expiry-alerts-daily': {
        'task': 'apps.core.tasks.check_expiry_alerts',
        'schedule': crontab(hour=8, minute=0),
    },
    'flag-overdue-returns-6h': {
        'task': 'apps.core.tasks.flag_overdue_returns',
        'schedule': crontab(minute=0, hour='*/6'),
    },
    'maintenance-notifier-weekly': {
        'task': 'apps.core.tasks.notify_upcoming_maintenance',
        'schedule': crontab(day_of_week=1, hour=9, minute=0),
    },
    'weekly-report': {
        'task': 'apps.core.tasks.generate_weekly_report',
        'schedule': crontab(day_of_week=1, hour=9, minute=30),
    },
}