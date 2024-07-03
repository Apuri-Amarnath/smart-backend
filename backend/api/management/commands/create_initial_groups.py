# your_app_name/management/commands/create_initial_groups.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from api.models import Fees_model, Bonafide, VerifySemesterRegistration, No_Dues_list


class Command(BaseCommand):
    help = 'Create initial groups and permissions'

    def handle(self, *args, **kwargs):
        caretaker_group, _ = Group.objects.get_or_create(name='Caretaker')
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        student_group, _ = Group.objects.get_or_create(name='Student')
        faculty_group, _ = Group.objects.get_or_create(name='Faculty')
        department_group, _ = Group.objects.get_or_create(name='Department')

        content_type = ContentType.objects.get_for_model(Fees_model)
        can_view_caretaker, _ = Permission.objects.get_or_create(
            codename='can_view_caretaker',
            name='Can view caretaker content',
            content_type=content_type,
        )
        can_view_admin, _ = Permission.objects.get_or_create(
            codename='can_view_admin',
            name='Can view admin content',
            content_type=content_type,
        )
        content_type_Bonafide = ContentType.objects.get_for_model(Bonafide)
        can_view_student, _ = Permission.objects.get_or_create(
            codename='can_view_student',
            name='Can view student content',
            content_type=content_type_Bonafide,
        )

        content_type_Faculty = ContentType.objects.get_for_model(VerifySemesterRegistration)
        can_view_faculty, _ = Permission.objects.get_or_create(
            codename='can_view_faculty',
            name='Can view faculty content',
            content_type=content_type_Faculty,
        )
        content_type_Department = ContentType.objects.get_for_model(No_Dues_list)
        can_view_department, _ = Permission.objects.get_or_create(
            codename='can_view_department',
            name='Can view department content',
            content_type=content_type_Department,
        )

        caretaker_group.permissions.add(can_view_caretaker)
        admin_group.permissions.add(can_view_admin)
        student_group.permissions.add(can_view_student)
        faculty_group.permissions.add(can_view_faculty)
        department_group.permissions.add(can_view_department)

        self.stdout.write(self.style.SUCCESS('Successfully created initial groups and permissions'))
