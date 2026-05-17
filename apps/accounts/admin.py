# file: apps/accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(UserAdmin):
    model           = Employee
    list_display    = ['name', 'email', 'role',
                        'company',
                          'is_active', 'date_joined']
    list_filter     = ['role', 'is_active',
                        'company'
                       ]
    search_fields   = ['name', 'email']
    ordering        = ['-date_joined']
    readonly_fields = ['date_joined', 'updated_at']
    fieldsets = (
        (None,         {'fields': ('email', 'password')}),
        ('Personal',   {'fields': ('name', 'company', 'department')}),
        ('Permissions',{'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Timestamps', {'fields': ('date_joined', 'updated_at')}),
    )
    add_fieldsets = ((None, {
        'classes': ('wide',),
        'fields': ('email', 'name', 'password1', 'password2', 'role', 'company'),
    }),)