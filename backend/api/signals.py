from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import User


@receiver(post_save, sender=User)
def assign_user_group(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'caretaker':
            caretaker_group = Group.objects.get(name='Caretaker')
            instance.groups.add(caretaker_group)
        elif instance.role == 'admin':
            admin_group = Group.objects.get(name='Admin')
            instance.groups.add(admin_group)
        elif instance.role == 'student':
            student_group = Group.objects.get(name='Student')
            instance.groups.add(student_group)
        elif instance.role == 'teacher':
            teacher_group = Group.objects.get(name='Teacher')
            instance.groups.add(teacher_group)
