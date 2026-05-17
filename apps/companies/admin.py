# file: apps/companies/admin.py
from django.contrib import admin
from .models import Company, Department


class DeptInline(admin.TabularInline):
    model  = Department
    extra  = 0
    fields = ['name', 'head']


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display  = ['name', 'industry', 'created_at']
    search_fields = ['name']
    inlines       = [DeptInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display  = ['name', 'company', 'head']
    list_filter   = ['company']
    search_fields = ['name']