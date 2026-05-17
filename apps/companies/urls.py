# file: apps/companies/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, DepartmentViewSet

router = DefaultRouter()
router.register('companies',   CompanyViewSet,    basename='company')
router.register('departments', DepartmentViewSet, basename='department')

urlpatterns = [path('', include(router.urls))]