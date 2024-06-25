from rest_framework import permissions, viewsets


class IsCaretakerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and (request.user.role == 'caretaker' or request.user.role == 'admin')


class IsStudentOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and (request.user.role == 'student' or request.user.role == 'admin')


class IsTeacherOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view):
        return request.user and (request.user.role == 'teacher' or request.user.role == 'admin')


class IsFacultyOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view):
        return request.user and (request.user.role == 'faculty' or request.user.role == 'admin')
