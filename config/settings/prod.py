# file: config/settings/prod.py
from .base import *
from decouple import config

DEBUG = False
ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', default='').split(',')

SECURE_PROXY_SSL_HEADER   = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE     = True
CSRF_COOKIE_SECURE        = True
SECURE_BROWSER_XSS_FILTER = True

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'