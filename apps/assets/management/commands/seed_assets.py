# file: apps/assets/management/commands/seed_assets.py
from django.core.management.base import BaseCommand
from apps.companies.models import Company
from apps.assets.models import Asset, AssetExpiry
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Seed sample assets for all companies'

    def handle(self, *args, **kwargs):
        for co in Company.objects.all():
            items = [
                dict(name=f'MacBook Pro ({co.name})', asset_type='laptop',   serial_no=f'LT-{co.id}-01', condition='new',  purchase_cost='150000', warranty_expiry=date.today()+timedelta(days=365)),
                dict(name=f'iPhone 15 ({co.name})',   asset_type='mobile',   serial_no=f'MB-{co.id}-01', condition='good', purchase_cost='80000',  warranty_expiry=date.today()+timedelta(days=180)),
                dict(name=f'MS Office ({co.name})',   asset_type='software', serial_no=None,              condition='new',  purchase_cost='12000',  warranty_expiry=None),
            ]
            for d in items:
                w = d.pop('warranty_expiry')
                asset, created = Asset.objects.get_or_create(
                    company=co, name=d['name'],
                    defaults={**d, 'status': 'available'}
                )
                if created and w:
                    AssetExpiry.objects.get_or_create(
                        asset=asset, expiry_type='warranty',
                        defaults={'expiry_date': w, 'days_before_alert': 30}
                    )
        self.stdout.write(self.style.SUCCESS('Assets seeded.'))