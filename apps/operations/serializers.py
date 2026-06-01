# file: apps/operations/serializers.py
from rest_framework import serializers
from .models import AssetTransfer, Maintenance


class AssetTransferSerializer(serializers.ModelSerializer):
    asset_name         = serializers.CharField(source='asset.name',         read_only=True)
    from_employee_name = serializers.CharField(source='from_employee.name', read_only=True)
    to_employee_name   = serializers.CharField(source='to_employee.name',   read_only=True)

    class Meta:
        model  = AssetTransfer
        fields = [
            'id', 'asset', 'asset_name',
            'from_employee', 'from_employee_name',
            'to_employee',   'to_employee_name',
            'reason', 'transferred_at',
        ]
        read_only_fields = ['id', 'transferred_at']

    def validate(self, data):
        if data.get('from_employee') == data.get('to_employee'):
            raise serializers.ValidationError('Cannot transfer to the same employee.')
        return data


class MaintenanceSerializer(serializers.ModelSerializer):
    asset_name = serializers.CharField(source='asset.name', read_only=True)

    class Meta:
        model  = Maintenance
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'asset_name']

    def validate(self, data):
        c = data.get('completed_date')
        s = data.get('scheduled_date') or (self.instance.scheduled_date if self.instance else None)
        if c and s and c < s:
            raise serializers.ValidationError('Completed date cannot be before scheduled date.')
        return data