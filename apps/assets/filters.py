# file: apps/assets/filters.py
import django_filters
from .models import Asset


class AssetFilter(django_filters.FilterSet):
    name            = django_filters.CharFilter(lookup_expr='icontains')
    serial_no       = django_filters.CharFilter(lookup_expr='icontains')
    warranty_before = django_filters.DateFilter(field_name='warranty_expiry', lookup_expr='lte')
    warranty_after  = django_filters.DateFilter(field_name='warranty_expiry', lookup_expr='gte')

    class Meta:
        model  = Asset
        fields = ['asset_type', 'status', 'condition', 'name', 'serial_no']