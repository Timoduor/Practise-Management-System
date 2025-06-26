from core.models import OrganisationRole  # Import here to avoid circular imports

ORG_ROLE_CHOICES = (
    ('SUPERADMIN', 'Super Admin'),
    ('ORGADMIN', 'Organisation Admin'),
    ('MANAGER', 'Manager'),
    ('EMPLOYEE', 'Employee'),
    ('VIEWER', 'Viewer'),
)

ROLE_HIERARCHY = {
    'SUPERADMIN': 4,
    'ORGADMIN': 3,
    'MANAGER': 2,
    'EMPLOYEE': 1,
    'VIEWER': 0,
}

ORG_ROLE_NAMES = [c[0] for c in ORG_ROLE_CHOICES]   #Role IDs from the choices

def has_minimum_role(user, org_id, minimum_role):
   
    user_roles = OrganisationRole.objects.filter(
        user=user, organisation_id=org_id, is_active=True
    ).values_list('role', flat=True)
    return any(ROLE_HIERARCHY.get(role, -1) >= ROLE_HIERARCHY[minimum_role] for role in user_roles)

    