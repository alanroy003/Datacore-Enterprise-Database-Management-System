# file: apps/core/serializers.py
from rest_framework import serializers
from .models import AuditLog, Report, SchedulerLog


class AuditLogSerializer(serializers.ModelSerializer):
    performed_by_name = serializers.CharField(source='performed_by.name', read_only=True, default=None)
    class Meta:
        model  = AuditLog
        fields = '__all__'
        read_only_fields = ['id', 'timestamp']


class ReportSerializer(serializers.ModelSerializer):
    generated_by_name = serializers.CharField(source='generated_by.name', read_only=True, default=None)
    class Meta:
        model  = Report
        fields = '__all__'
        read_only_fields = ['id', 'generated_at', 'generated_by']


class SchedulerLogSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SchedulerLog
        fields = '__all__'