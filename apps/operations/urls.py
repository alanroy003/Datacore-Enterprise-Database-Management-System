# file: apps/operations/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssetTransferViewSet, MaintenanceViewSet

router = DefaultRouter()
router.register('transfers',   AssetTransferViewSet, basename='transfer')
router.register('maintenance', MaintenanceViewSet,   basename='maintenance')

urlpatterns = [path('', include(router.urls))]