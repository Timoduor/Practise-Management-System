# core/permissions/organisation_permissions.py
from .base_permissions import BaseRolePermission
from core.models.organisation_role import OrganisationRole


class MinimumViewer(BaseRolePermission):
    """
    Allows users with at least 'VIEWER' role.
    """
    minimum_required_role = 'VIEWER'

class MinimumEmployee(BaseRolePermission):
    """
    Allows users with at least 'EMPLOYEE' role.
    """
    minimum_required_role = 'EMPLOYEE'

class MinimumManager(BaseRolePermission):
    """
    Allows users with at least 'MANAGER' role.
    """
    minimum_required_role = 'MANAGER'

class MinimumOrgAdmin(BaseRolePermission):
    """
    Allows users with at least 'ORGADMIN' role.
    """
    minimum_required_role = 'ORGADMIN'

class MinimumSuperAdmin(BaseRolePermission):
    """
    Allows users with at least 'SUPERADMIN' role.
    """
    minimum_required_role = 'SUPERADMIN'

    