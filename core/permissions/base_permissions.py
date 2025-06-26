# core/permissions/base_permissions.py
import logging
logger = logging.getLogger(__name__)
from rest_framework.permissions import BasePermission
from core.models.organisation_role import OrganisationRole
from rest_framework.permissions import SAFE_METHODS


ROLE_HIERARCHY = {
    'SUPERADMIN': 4,
    'ORGADMIN': 3,
    'MANAGER': 2,
    'EMPLOYEE': 1,
    'VIEWER': 0,
}



def get_org_id(request, view):
    return (
        view.kwargs.get('org_pk')
        or view.kwargs.get('pk')
        or request.data.get('organisation')
        or request.query_params.get('organisation')
    )
class BaseRolePermission(BasePermission):
    """
    Base permission class to check user roles within an organization.
    """
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if OrganisationRole.objects.filter(user=request.user, role='SUPERADMIN', is_active=True).exists():
            return True
        org_id = view.kwargs.get('org_pk') or view.kwargs.get('pk')
        allowed = self.check_role(request.user, org_id)
        if not allowed:
            logger.warning(f"Permission denied: user={request.user.pk}, org_id={org_id}, role={self.__class__.__name__}")
            return allowed
        return self.check_role(request.user, org_id)

    def check_role(self, user, org_id):
        from core.utils.permissions import has_minimum_role  # Import here to avoid circular dependency

        if not self.minimum_required_role:
           raise NotImplementedError("Define minimum_required_role in subclass")
    
        return has_minimum_role(user, org_id, self.minimum_required_role)
    

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        """
        Check if the user has permission to access the object.
        This method is called for object-level permissions.
        """
        org_id = view.kwargs.get('org_pk') or view.kwargs.get('pk')
        return self.check_role(request.user, org_id)

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
    
def get_org_id_from_obj(obj):
    """
    Helper to get organisation id from object.
    Adjust based on your model fields.
    """
    # Common pattern: obj.organisation_id or obj.organisation.id
    if hasattr(obj, 'organisation_id'):
        return obj.organisation_id
    elif hasattr(obj, 'organisation') and obj.organisation:
        return obj.organisation.id
    return None


class HierarchicalObjectPermission(BasePermission):
    """
    Base class for object-level permission using ROLE_HIERARCHY.
    Subclasses must set `required_min_role` attribute.
    """

    required_min_role = None  # e.g. 'MANAGER'

    def get_user_role_level(self, user, org_id):
        if user.is_superuser:
            return ROLE_HIERARCHY['SUPERADMIN']

        roles = OrganisationRole.objects.filter(
            user=user, organisation_id=org_id, is_active=True
        ).values_list('role', flat=True)

        # Return highest role level for the user in the org
        return max([ROLE_HIERARCHY.get(role, -1) for role in roles], default=-1)

    def has_object_permission(self, request, view, obj):
        if not self.required_min_role:
            raise NotImplementedError("Define required_min_role in subclass")

        org_id = get_org_id_from_obj(obj)
        if not org_id:
            return False  # Cannot check permissions without org ID

        user_level = self.get_user_role_level(request.user, org_id)
        required_level = ROLE_HIERARCHY[self.required_min_role]

        return user_level >= required_level


        