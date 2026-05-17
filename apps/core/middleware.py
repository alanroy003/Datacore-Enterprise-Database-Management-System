# file: apps/core/middleware.py
import threading
_thread_locals = threading.local()

class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.user = getattr(request, 'user', None)
        _thread_locals.ip   = self._get_ip(request)
        return self.get_response(request)

    @staticmethod
    def _get_ip(request):
        fwd = request.META.get('HTTP_X_FORWARDED_FOR')
        return fwd.split(',')[0].strip() if fwd else request.META.get('REMOTE_ADDR')

def get_current_user():
    return getattr(_thread_locals, 'user', None)