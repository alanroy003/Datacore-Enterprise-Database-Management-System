# file: apps/companies/models.py
from django.db import models
from django.conf import settings


class Company(models.Model):
    name       = models.CharField(max_length=255, unique=True)
    industry   = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Companies'

    def __str__(self): return self.name


class Department(models.Model):
    company    = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='departments')
    name       = models.CharField(max_length=255)
    head       = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='headed_department'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('company', 'name')]
        ordering = ['name']

    def __str__(self): return f"{self.name} — {self.company.name}"