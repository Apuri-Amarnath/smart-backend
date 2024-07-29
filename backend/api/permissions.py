from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets
from .models import College


class IsCollegeMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        college_id = view.kwargs['college']
        return request.user.college.id == int(college_id)


class IsCaretakerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        is_same_college = IsCollegeMember().has_permission(request, view)
        return is_same_college and (request.user.role in ['caretaker', 'super-admin'])


class IsStudentOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        is_same_college = IsCollegeMember().has_permission(request, view)
        return is_same_college and (request.user.role in ['student', 'super-admin'])


class IsTeacherOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in ['teacher', 'super-admin']


class IsFacultyOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in ['faculty', 'super-admin']


class IsDepartmentOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in ['department', 'super-admin']


class IsOfficeOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in ['office', 'super-admin']


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 'super-admin'
