# file: apps/assets/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone


class AssetType(models.TextChoices):
    LAPTOP    = 'laptop',    'Laptop'
    MOBILE    = 'mobile',    'Mobile'
    SOFTWARE  = 'software',  'Software'
    FURNITURE = 'furniture', 'Furniture'
    VEHICLE   = 'vehicle',   'Vehicle'
    OTHER     = 'other',     'Other'


class Condition(models.TextChoices):
    NEW  = 'new',  'New'
    GOOD = 'good', 'Good'
    FAIR = 'fair', 'Fair'
    POOR = 'poor', 'Poor'


class AssetStatus(models.TextChoices):
    AVAILABLE      = 'available',      'Available'
    ASSIGNED       = 'assigned',       'Assigned'
    IN_MAINTENANCE = 'in_maintenance', 'In Maintenance'
    RETIRED        = 'retired',        'Retired'


class ExpiryType(models.TextChoices):
    WARRANTY  = 'warranty',  'Warranty'
    LICENSE   = 'license',   'License'
    INSURANCE = 'insurance', 'Insurance'
    OTHER     = 'other',     'Other'


class Asset(models.Model):
    company       = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='assets')
    name          = models.CharField(max_length=255)
    asset_type    = models.CharField(max_length=20, choices=AssetType.choices, default=AssetType.OTHER)
    serial_no     = models.CharField(max_length=255, unique=True, null=True, blank=True)
    condition     = models.CharField(max_length=10, choices=Condition.choices, default=Condition.NEW)
    status        = models.CharField(max_length=20, choices=AssetStatus.choices, default=AssetStatus.AVAILABLE)
    purchase_date   = models.DateField(null=True, blank=True)
    warranty_expiry = models.DateField(null=True, blank=True)
    purchase_cost   = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes           = models.TextField(blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self): return f"{self.name} ({self.serial_no or 'no-sn'})"

    @property
    def is_under_warranty(self):
        return bool(self.warranty_expiry and self.warranty_expiry >= timezone.now().date())

    @property
    def current_holder(self):
        return self.logs.filter(returned_at__isnull=True).select_related('employee').first()


class AssetLog(models.Model):
    asset                = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='logs')
    employee             = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='asset_logs')
    checked_out_at       = models.DateTimeField(auto_now_add=True)
    expected_return_date = models.DateField(null=True, blank=True)
    returned_at          = models.DateTimeField(null=True, blank=True)
    condition_on_return  = models.CharField(max_length=10, choices=Condition.choices, null=True, blank=True)
    notes                = models.TextField(blank=True)

    class Meta:
        ordering = ['-checked_out_at']

    @property
    def is_active(self):  return self.returned_at is None

    @property
    def is_overdue(self):
        return self.is_active and bool(
            self.expected_return_date and
            self.expected_return_date < timezone.now().date()
        )


class AssetExpiry(models.Model):
    asset             = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='expiries')
    expiry_type       = models.CharField(max_length=20, choices=ExpiryType.choices)
    expiry_date       = models.DateField()
    alert_sent        = models.BooleanField(default=False)
    days_before_alert = models.IntegerField(default=30)
    created_at        = models.DateTimeField(auto_now_add=True)



    class Meta:
        unique_together = [('asset', 'expiry_type')]
        ordering = ['expiry_date']