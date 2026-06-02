# file: apps/core/exceptions.py
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.exceptions import (
    ValidationError, NotFound, PermissionDenied,
    AuthenticationFailed, NotAuthenticated,
)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        if   isinstance(exc, ValidationError):                         msg = 'Validation failed.'
        elif isinstance(exc, NotFound):                                msg = 'Resource not found.'
        elif isinstance(exc, PermissionDenied):                        msg = 'Permission denied.'
        elif isinstance(exc, (AuthenticationFailed, NotAuthenticated)): msg = 'Authentication required.'
        else:                                                           msg = str(exc)

        response.data = {
            'success': False,
            'error': {
                'code':    response.status_code,
                'message': msg,
                'details': response.data,
            }
        }
    else:
        response = Response({
            'success': False,
            'error': {'code': 500, 'message': 'Unexpected server error.', 'details': str(exc)}
        }, status=500)

    return response