# file: apps/notifications/services.py
from .models import Notification


class NotificationService:
    @staticmethod
    def create(employee, notification_type, title, message):
        return Notification.objects.create(
            employee=employee, notification_type=notification_type,
            title=title, message=message,
        )

    @staticmethod
    def create_bulk(employees, notification_type, title, message):
        return Notification.objects.bulk_create([
            Notification(employee=e, notification_type=notification_type, title=title, message=message)
            for e in employees
        ])