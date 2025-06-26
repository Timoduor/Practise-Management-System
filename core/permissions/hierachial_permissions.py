from rest_framework.permissions import BasePermission, IsAuthenticated
from core.models.organisation_role import OrganisationRole
from core.utils.permissions import get_organisation_id_from_request  # Adjust import based on your project structure

class HierarchicalOrgPermission(BasePermission):
    """
    Permission class enforcing hierarchical role-based access:
    - Django superuser: unrestricted access
    - SUPERADMIN: full access to all orgs
    - ORGADMIN: full access within their org
    - MANAGER: limited write + read
    - EMPLOYEE: mostly read + limited write
    - VIEWER: read-only
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # Allow django superuser full unrestricted access
        if getattr(user, 'is_superuser', False):
            return True

        org_id = get_organisation_id_from_request(view, request, getattr(view, 'get_object', lambda: None)())

        # SUPERADMIN: full access everywhere
        if OrganisationRole.objects.filter(user=user, role='SUPERADMIN', is_active=True).exists():
            return True

        if not org_id:
            return False  # No org context, deny access

        # ORGADMIN full access in org
        if OrganisationRole.objects.filter(user=user, organisation_id=org_id, role='ORGADMIN', is_active=True).exists():
            return True

        # MANAGER limited write + read in org
        if OrganisationRole.objects.filter(user=user, organisation_id=org_id, role='MANAGER', is_active=True).exists():
            if view.action in ['list', 'retrieve', 'create', 'update', 'partial_update']:
                return True
            if view.action == 'destroy':
                return False

        # EMPLOYEE mostly read + limited write
        if OrganisationRole.objects.filter(user=user, organisation_id=org_id, role='EMPLOYEE', is_active=True).exists():
            if view.action in ['list', 'retrieve', 'partial_update']:
                return True
            return False

        # VIEWER read-only
        if OrganisationRole.objects.filter(user=user, organisation_id=org_id, role='VIEWER', is_active=True).exists():
            if view.action in ['list', 'retrieve']:
                return True
            return False

        # Default deny
        return False


