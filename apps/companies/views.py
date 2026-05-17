# file: apps/companies/views.py
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .models import Company, Department
from .serializers import CompanySerializer, DepartmentSerializer
from apps.accounts.permissions import IsSuperAdmin, IsAdminOrAbove


@extend_schema(tags=['companies'])
class CompanyViewSet(ModelViewSet):
    serializer_class = CompanySerializer
    search_fields    = ['name', 'industry']

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [IsSuperAdmin()]
        if self.action in ['update', 'partial_update']:
            return [IsAdminOrAbove()]
        return [IsAuthenticated()]

    def get_queryset(self):
        u = self.request.user
        return Company.objects.all() if u.is_superadmin else Company.objects.filter(id=u.company_id)


@extend_schema(tags=['companies'])
class DepartmentViewSet(ModelViewSet):
    serializer_class = DepartmentSerializer
    search_fields    = ['name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrAbove()]
        return [IsAuthenticated()]

    def get_queryset(self):
        u  = self.request.user
        qs = Department.objects.select_related('company', 'head')
        return qs.all() if u.is_superadmin else qs.filter(company=u.company)

    def perform_create(self, serializer):
        if self.request.user.is_superadmin:
            serializer.save()
        else:
            serializer.save(company=self.request.user.company)