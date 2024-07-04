from django.core.management.base import BaseCommand
from api.models import Departments_for_no_Dues


class Command(BaseCommand):
    help = 'Adds all departments for No due requests '

    def handle(self, *args, **options):
        default_departments = [
            {
                'Department_id': 1,
                'Department_name': 'Electrical & Electronics Laboratory',
                'status': 'pending',
            },
            {
                'Department_id': 2,
                'Department_name': 'Physics Laboratory',
                'status': 'pending',
            },
            {
                'Department_id': 3,
                'Department_name': 'Chemistry Laboratory',
                'status': 'pending',

            },
            {
                'Department_id': 4,
                'Department_name': 'Mechanics Laboratory',
                'status': 'pending',

            },
            {
                'Department_id': 5,
                'Department_name': 'Civil Lab',
                'status': 'pending',

            },
            {
                'Department_id': 6,
                'Department_name': 'Workshop',
                'status': 'pending',

            },
            {
                'Department_id': 7,
                'Department_name': 'Computer Laboratory',
                'status': 'pending',

            },
            {
                'Department_id': 8,
                'Department_name': 'KYP Lab/BSDM',
                'status': 'pending',

            },
            {
                'Department_id': 9,
                'Department_name': 'TEQIP',
                'status': 'pending',

            },
            {
                'Department_id': 10,
                'Department_name': 'Examination Section',
                'status': 'pending',

            },
            {
                'Department_id': 11,
                'Department_name': 'Sports Section',
                'status': 'pending',

            },
            {
                'Department_id': 12,
                'Department_name': 'General Store',
                'status': 'pending',

            },
            {
                'Department_id': 13,
                'Department_name': 'Hostel',
                'status': 'pending',

            },
            {
                'Department_id': 14,
                'Department_name': 'Library',
                'status': 'pending',

            },
            {
                'Department_id': 15,
                'Department_name': 'Academic Section',
                'status': 'pending',

            },
            {
                'Department_id': 16,
                'Department_name': 'Cash Section',
                'status': 'pending',

            },
            {
                'Department_id': 17,
                'Department_name': 'Accounts Section',
                'status': 'pending',

            },
            {
                'Department_id': 18,
                'Department_name': 'HoD, EEE / ME / CSE / CE / CSE-AI / CE with CA',
                'status': 'pending',

            },
        ]

        for department_data in default_departments:
            department, created = Departments_for_no_Dues.objects.get_or_create(
                Department_name=department_data['Department_name'],
                defaults={
                    'status': department_data['status'],
                    'approved_date': None,
                    'applied_date': None,
                }
            )
        self.stdout.write(self.style.SUCCESS('departments populated successfully'))
