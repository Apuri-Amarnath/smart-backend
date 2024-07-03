from django.core.management.base import BaseCommand
from api.models import Departments_for_no_Dues


class Command(BaseCommand):
    help = 'Adds all departments for No due requests '

    def handle(self, *args, **options):
        default_departments = [
            {
                'Department_name': 'Electrical & Electronics Laboratory',
                'status': 'pending',
                'approved': False,
            },
            {
                'Department_name': 'Physics Laboratory',
                'status': 'pending',
                'approved': False,
            },
            {
                'Department_name': 'Chemistry Laboratory',
                'status': 'pending',
                'approved': False,
            },
            {
                'Department_name': 'Mechanics Laboratory',
                'status': 'pending',
                'approved': False,
            },
            {
                'Department_name': 'Civil Lab',
                'status': 'pending',
                'approved': False,
            },
            {
                'Department_name': 'Workshop',
                'status': 'pending',
                'approved': False,
            },
            {
                'Department_name': 'Computer Laboratory',
                'status': 'pending',
                'approved': False,
            },
            {
                'Department_name': 'KYP Lab/BSDM',
                'status': 'pending',
                'approved': False,
            },
            {
                'Department_name': 'TEQIP',
                'status': 'pending',
                'approved': False,
            },
            {
                'Department_name': 'Examination Section',
                'status': 'pending',
                'approved': False,
            },
            {
                'Department_name': 'Sports Section',
                'status': 'pending',
                'approved': False,
            },
            {
                'Department_name': 'General Store',
                'status': 'pending',
                'approved': False,
            },
            {
                'Department_name': 'Hostel',
                'status': 'pending',
                'approved': False,
            },
            {
                'Department_name': 'Library',
                'status': 'pending',
                'approved': False,
            },
            {
                'Department_name': 'Academic Section',
                'status': 'pending',
                'approved': False,
            },
            {
                'Department_name': 'Cash Section',
                'status': 'pending',
                'approved': False,
            },
            {
                'Department_name': 'Accounts Section',
                'status': 'pending',
                'approved': False,
            },
            {
                'Department_name': 'HoD, EEE / ME / CSE / CE / CSE-AI / CE with CA',
                'status': 'pending',
                'approved': False,
            },
        ]

        for department_data in default_departments:
            Departments_for_no_Dues.objects.get_or_create(
                Department_name=department_data['Department_name'],
                defaults={
                    'status': department_data['status'],
                    'approved': department_data['approved'],
                    'approved_date':None,

                    'applied_date': None,
                }
        )
        self.stdout.write(self.style.SUCCESS('departments populated successfully'))
