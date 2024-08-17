from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from api.models import Fees_model, Bonafide, VerifySemesterRegistration, No_Dues_list, HostelRooms, College_with_Ids
from django.apps import apps
class Command(BaseCommand):
    help = 'Create initial groups and permissions'

    def handle(self, *args, **kwargs):
        caretaker_group, _ = Group.objects.get_or_create(name='Caretaker')
        admin_group, _ = Group.objects.get_or_create(name='Super-Admin')
        student_group, _ = Group.objects.get_or_create(name='Student')
        faculty_group, _ = Group.objects.get_or_create(name='Faculty')
        department_group, _ = Group.objects.get_or_create(name='Department')
        office_group, _ = Group.objects.get_or_create(name='Office')
        hod_group, _ = Group.objects.get_or_create(name='HOD')

        content_type_caretaker_fees = ContentType.objects.get_for_model(Fees_model)
        content_type_caretaker_hostel = ContentType.objects.get_for_model(HostelRooms)
        content_type_Bonafide = ContentType.objects.get_for_model(Bonafide)
        content_type_Faculty = ContentType.objects.get_for_model(VerifySemesterRegistration)
        content_type_Department = ContentType.objects.get_for_model(No_Dues_list)
        content_type_hod = ContentType.objects.get_for_model(VerifySemesterRegistration)
        content_type_office = ContentType.objects.get_for_model(College_with_Ids)

        can_view_caretaker_fees, _ = Permission.objects.get_or_create(
            codename='can_view_caretaker',
            name='Can view caretaker content',
            content_type=content_type_caretaker_fees,
        )
        can_view_caretaker_hostel, _ = Permission.objects.get_or_create(
            codename='can_view_caretaker_hostel',
            name='Can view caretaker hostel content',
            content_type=content_type_caretaker_hostel,
        )
        can_view_hod,_ = Permission.objects.get_or_create(
            codename='can_view_hod',
            name='Can view hod content',
            content_type=content_type_hod,

        )
        can_view_student, _ = Permission.objects.get_or_create(
            codename='can_view_student',
            name='Can view student content',
            content_type=content_type_Bonafide,
        )

        can_view_faculty, _ = Permission.objects.get_or_create(
            codename='can_view_faculty',
            name='Can view faculty content',
            content_type=content_type_Faculty,
        )
        can_view_department, _ = Permission.objects.get_or_create(
            codename='can_view_department',
            name='Can view department content',
            content_type=content_type_Department,
        )
        can_view_Office, _ = Permission.objects.get_or_create(
            codename='can_view_Office',
            name='Can view office content',
            content_type=content_type_office,
        )

        caretaker_group.permissions.add(can_view_caretaker_fees)
        caretaker_group.permissions.add(can_view_caretaker_hostel)
        student_group.permissions.add(can_view_student)
        faculty_group.permissions.add(can_view_faculty)
        department_group.permissions.add(can_view_department)
        office_group.permissions.add(can_view_Office)
        hod_group.permissions.add(can_view_hod)

        for model in apps.get_models():
            content_type = ContentType.objects.get_for_model(model)
            permissions = Permission.objects.filter(content_type=content_type)
            for permission in permissions:
                admin_group.permissions.add(permission)

        self.stdout.write(self.style.SUCCESS('Successfully created initial groups and permissions'))
