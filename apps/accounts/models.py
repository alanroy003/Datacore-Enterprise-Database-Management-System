# file: apps/accounts/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class Role(models.TextChoices):
    SUPERADMIN = 'superadmin', 'Super Admin'
    ADMIN      = 'admin',      'Admin'
    MANAGER    = 'manager',    'Manager'
    EMPLOYEE   = 'employee',   'Employee'


class EmployeeManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra):
        if not email:
            raise ValueError('Email is required')
        user = self.model(email=self.normalize_email(email), name=name, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        extra.setdefault('role', Role.SUPERADMIN)
        return self.create_user(email, name, password, **extra)


class Employee(AbstractBaseUser, PermissionsMixin):
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='employees'
    )
    department = models.ForeignKey(
        'companies.Department',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='employees'
    )
    email       = models.EmailField(unique=True)
    name        = models.CharField(max_length=255)
    role        = models.CharField(max_length=20, choices=Role.choices, default=Role.EMPLOYEE)
    is_active   = models.BooleanField(default=True)
    is_staff    = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    objects = EmployeeManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.name} ({self.email})"

    @property
    def is_superadmin(self): return self.role == Role.SUPERADMIN

    @property
    def is_admin(self): return self.role in [Role.SUPERADMIN, Role.ADMIN]

    @property
    def is_manager(self): return self.role in [Role.SUPERADMIN, Role.ADMIN, Role.MANAGER]