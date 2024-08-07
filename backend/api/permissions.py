from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets
from .models import College

import logging

logger = logging.getLogger(__name__)


class IsCollegeMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        college_slug = view.kwargs.get('slug')
        try:
            college = College.objects.get(slug=college_slug)
        except College.DoesNotExist:
            return False
        logger.debug(f"User College ID: {request.user.college.id}, Requested College ID: {college.id}")
        return request.user.college.id == college.id


class IsCaretakerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        is_same_college = IsCollegeMember().has_permission(request, view)
        if not is_same_college:
            return False
        return is_same_college and (request.user.role in ['caretaker', 'super-admin'])


class IsRegistrarOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        is_same_college = IsCollegeMember().has_permission(request, view)
        if not is_same_college:
            return False
        return is_same_college and (request.user.role in ['registrar', 'super-admin'])


class IsStudentOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        is_same_college = IsCollegeMember().has_permission(request, view)
        if not is_same_college:
            return False
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
        is_same_college = IsCollegeMember().has_permission(request, view)
        if not is_same_college:
            return False
        return request.user.role in ['office', 'super-admin']


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 'super-admin'
