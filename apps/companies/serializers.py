# file: apps/companies/serializers.py
from rest_framework import serializers
from .models import Company, Department


class CompanySerializer(serializers.ModelSerializer):
    employee_count   = serializers.SerializerMethodField()
    department_count = serializers.SerializerMethodField()

    class Meta:
        model  = Company
        fields = ['id', 'name', 'industry', 'employee_count', 'department_count', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_employee_count(self, obj):   return obj.employees.filter(is_active=True).count()
    def get_department_count(self, obj): return obj.departments.count()


class DepartmentSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    head_name    = serializers.CharField(source='head.name',    read_only=True, default=None)

    class Meta:
        model  = Department
        fields = ['id', 'name', 'company', 'company_name', 'head', 'head_name', 'created_at']
        read_only_fields = ['id', 'created_at']