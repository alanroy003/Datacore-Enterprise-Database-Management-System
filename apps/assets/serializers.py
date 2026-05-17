# file: apps/assets/serializers.py
from rest_framework import serializers
from django.utils import timezone
from .models import Asset, AssetLog, AssetExpiry


class AssetExpirySerializer(serializers.ModelSerializer):
    class Meta:
        model  = AssetExpiry
        fields = '__all__'
        read_only_fields = ['id', 'alert_sent', 'created_at']

    def validate_expiry_date(self, value):
        if not self.instance and value < timezone.now().date():
            raise serializers.ValidationError('Expiry date cannot be in the past.')
        return value


class AssetLogSerializer(serializers.ModelSerializer):
    asset_name    = serializers.CharField(source='asset.name',    read_only=True)
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    is_active     = serializers.BooleanField(read_only=True)
    is_overdue    = serializers.BooleanField(read_only=True)

    class Meta:
        model  = AssetLog
        fields = '__all__'
        read_only_fields = ['id', 'checked_out_at']


class AssetSerializer(serializers.ModelSerializer):
    is_under_warranty   = serializers.BooleanField(read_only=True)
    current_holder_name = serializers.SerializerMethodField()
    company_name        = serializers.CharField(source='company.name', read_only=True)
    expiries            = AssetExpirySerializer(many=True, read_only=True)

    class Meta:
        model  = Asset
        fields = [
            'id', 'company', 'company_name', 'name', 'asset_type',
            'serial_no', 'condition', 'status', 'purchase_date',
            'warranty_expiry', 'purchase_cost', 'notes',
            'is_under_warranty', 'current_holder_name',
            'expiries', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_current_holder_name(self, obj):
        h = obj.current_holder
        return h.employee.name if h else None

    def validate_serial_no(self, value):
        if value:
            qs = Asset.objects.filter(serial_no=value)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError('Serial number already exists.')
        return value


class AssetCheckoutSerializer(serializers.Serializer):
    employee_id          = serializers.IntegerField()
    expected_return_date = serializers.DateField(required=False, allow_null=True)


class AssetReturnSerializer(serializers.Serializer):
    condition_on_return = serializers.ChoiceField(choices=['new', 'good', 'fair', 'poor'])
    notes               = serializers.CharField(required=False, allow_blank=True, default='')