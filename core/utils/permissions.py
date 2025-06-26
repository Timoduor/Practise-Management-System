# from rest_framework import permissions
from rest_framework.permissions import BasePermission, SAFE_METHODS
from core.models.organisation_role import OrganisationRole

class IsEntityMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.entity == request.user.employee.entity and obj.unit == request.user.employee.unit


def get_organisation_id_from_request(viewset, request, obj=None):
    # 1. Try to get organisation ID from URL kwargs
    org_id = viewset.kwargs.get('organisation_pk')
    if org_id:
        return org_id

    # 2. Try to get organisation ID from request data (POST/PUT/PATCH body)
    org_id = request.data.get('organisation') or request.data.get('organisation_id')
    if org_id:
        return org_id

    # 3. Try to get organisation ID from the object itself (if provided)
    if obj and hasattr(obj, 'organisation_id'):
        return obj.organisation_id

    if obj and hasattr(obj, 'organisation'):
        return obj.organisation.id if hasattr(obj.organisation, 'id') else obj.organisation.pk

    # 4. Fallback if nothing found
    return None


def has_permission_code(user, org_id, permission_code):
    roles = OrganisationRole.objects.filter(
        user=user, organisation_id=org_id, is_active=True
    ).select_related('permission_profile')

    for role in roles:
        if not role.permission_profile:
            continue
        if role.permission_profile.permissions.filter(code=permission_code).exists():
            return True
    return False
