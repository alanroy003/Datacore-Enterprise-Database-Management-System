# file: apps/core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuditLogViewSet, ReportViewSet

router = DefaultRouter()
router.register('audit-logs', AuditLogViewSet, basename='audit-log')
router.register('reports',    ReportViewSet,   basename='report')

urlpatterns = [path('', include(router.urls))]