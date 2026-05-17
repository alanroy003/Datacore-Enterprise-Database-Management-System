# file: apps/accounts/permissions.py
from rest_framework.permissions import BasePermission
from .models import Role


class IsSuperAdmin(BasePermission):
    message = 'Super admin access required.'
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == Role.SUPERADMIN


class IsAdminOrAbove(BasePermission):
    message = 'Admin access required.'
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsManagerOrAbove(BasePermission):
    message = 'Manager access required.'
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_manager