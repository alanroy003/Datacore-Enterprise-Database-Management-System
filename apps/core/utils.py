# file: apps/core/utils.py
def success_response(data, message=''):
    return {'success': True, 'message': message, 'data': data}

def error_response(message, details=None):
    return {'success': False, 'error': {'message': message, 'details': details or {}}}