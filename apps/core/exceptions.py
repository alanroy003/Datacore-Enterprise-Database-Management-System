# file: apps/core/exceptions.py
from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    return exception_handler(exc, context)  # upgraded in Module 5