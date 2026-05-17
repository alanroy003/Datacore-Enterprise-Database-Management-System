# file: apps/companies/management/commands/seed_data.py
from django.core.management.base import BaseCommand
from apps.companies.models import Company, Department
from apps.accounts.models import Employee, Role


class Command(BaseCommand):
    help = 'Seed companies, departments, and test users'

    def handle(self, *args, **kwargs):
        co_a, _ = Company.objects.get_or_create(name='Acme Corp', defaults={'industry': 'Technology'})
        co_b, _ = Company.objects.get_or_create(name='Beta Ltd',  defaults={'industry': 'Finance'})

        for co in [co_a, co_b]:
            for name in ['Engineering', 'HR', 'Finance']:
                Department.objects.get_or_create(company=co, name=name)

        test_users = [
            ('admin@acme.com',   'Acme Admin',    Role.ADMIN,    co_a),
            ('manager@acme.com', 'Acme Manager',  Role.MANAGER,  co_a),
            ('emp@acme.com',     'Acme Employee', Role.EMPLOYEE, co_a),
            ('admin@beta.com',   'Beta Admin',    Role.ADMIN,    co_b),
        ]
        for email, name, role, co in test_users:
            if not Employee.objects.filter(email=email).exists():
                Employee.objects.create_user(
                    email=email, name=name,
                    password='Test@1234', role=role, company=co
                )

        self.stdout.write(self.style.SUCCESS('Seed complete.'))