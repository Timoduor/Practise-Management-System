# from rest_framework import permissions
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsEntityMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.entity == request.user.employee.entity and obj.unit == request.user.employee.unit
class ReadOnlyUnlessSuperadmin(BasePermission):
    """
    Allows read-only access to all users.
    Only superadmins can create, update, or delete.
    """
    def has_permission(self, request, view):
        # If it's a safe (read) method, allow everyone
        if request.method in SAFE_METHODS:  # ['GET', 'HEAD', 'OPTIONS']
            return True

        # Otherwise, only allow if user is staff *and* superadmin
        return (
            request.user.is_staff
            and hasattr(request.user, "admin_user")
            and request.user.admin_user.admin_type.name == "SUP"
        )