from rest_framework.permissions import BasePermission
from core.utils.permissions import has_permission_code, get_organisation_id_from_request
from core.permissions.base_permissions import get_org_id_from_obj

class HasModularPermission(BasePermission):
    required_permission_code = None

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        org_id = get_organisation_id_from_request(view, request, getattr(view, 'get_object', lambda: None)())
        if not org_id or not self.required_permission_code:
            return False

        return has_permission_code(request.user, org_id, self.required_permission_code)

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        org_id = get_org_id_from_obj(obj)
        if not org_id:
            return False

        return has_permission_code(request.user, org_id, self.required_permission_code)



class CanInviteUsers(HasModularPermission):
    required_permission_code = 'can_invite_users'


    