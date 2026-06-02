# file: apps/core/utils.py
def success_response(data, message=''):
    return {'success': True, 'message': message, 'data': data}


def error_response(message, details=None):
    return {'success': False, 'error': {'message': message, 'details': details or {}}}


def log_scheduler_run(job_name, status, records=0, error=''):
    from .models import SchedulerLog
    SchedulerLog.objects.create(
        job_name=job_name, status=status,
        records_processed=records, error_message=error,
    )