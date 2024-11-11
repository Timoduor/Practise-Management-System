from rest_framework import permissions

class IsEntityMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.entity == request.user.employee.entity and obj.unit == request.user.employee.unit