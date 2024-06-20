from django.core.management.base import BaseCommand
from api.models import Departments_for_no_due


class Command(BaseCommand):
    help = 'Adds all departments for No due requests '

    def handle(self, *args, **options):
        default_departments = [
            {
                'Department_name': 'Electrical & Electronics Laboratory',
                'status': 'waiting for approval',  # Default status
                'approved': False,  # Default approved status
            },
            {
                'Department_name': 'Physics Laboratory',
                'status': 'waiting for approval',
                'approved': False,
            },
            {
                'Department_name': 'Chemistry Laboratory',
                'status': 'waiting for approval',
                'approved': False,
            },
            {
                'Department_name': 'Mechanics Laboratory',
                'status': 'waiting for approval',
                'approved': False,
            },
            {
                'Department_name': 'Civil Lab',
                'status': 'waiting for approval',
                'approved': False,
            },
            {
                'Department_name': 'Workshop',
                'status': 'waiting for approval',
                'approved': False,
            },
            {
                'Department_name': 'Computer Laboratory',
                'status': 'waiting for approval',
                'approved': False,
            },
            {
                'Department_name': 'KYP Lab/BSDM',
                'status': 'waiting for approval',
                'approved': False,
            },
            {
                'Department_name': 'TEQIP',
                'status': 'waiting for approval',
                'approved': False,
            },
            {
                'Department_name': 'Examination Section',
                'status': 'waiting for approval',
                'approved': False,
            },
            {
                'Department_name': 'Sports Section',
                'status': 'waiting for approval',
                'approved': False,
            },
            {
                'Department_name': 'General Store',
                'status': 'waiting for approval',
                'approved': False,
            },
            {
                'Department_name': 'Hostel',
                'status': 'waiting for approval',
                'approved': False,
            },
            {
                'Department_name': 'Library',
                'status': 'waiting for approval',
                'approved': False,
            },
            {
                'Department_name': 'Academic Section',
                'status': 'waiting for approval',
                'approved': False,
            },
            {
                'Department_name': 'Cash Section',
                'status': 'waiting for approval',
                'approved': False,
            },
            {
                'Department_name': 'Accounts Section',
                'status': 'waiting for approval',
                'approved': False,
            },
            {
                'Department_name': 'HoD, EEE / ME / CSE / CE / CSE-AI / CE with CA',
                'status': 'waiting for approval',
                'approved': False,
            },
        ]

        for department_data in default_departments:
            Departments_for_no_due.objects.get_or_create(
                Department_name=department_data['Department_name'],
                defaults={
                    'status': department_data['status'],
                    'approved': department_data['approved'],
                    'approved_date':None,

                    'applied_date': None,
                }
        )
        self.stdout.write(self.style.SUCCESS('departments populated successfully'))
