# file: apps/assets/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssetViewSet, AssetLogViewSet, AssetExpiryViewSet

router = DefaultRouter()
router.register('assets',         AssetViewSet,       basename='asset')
router.register('asset-logs',     AssetLogViewSet,    basename='asset-log')
router.register('asset-expiries', AssetExpiryViewSet, basename='asset-expiry')


urlpatterns = [path('', include(router.urls))]