# filepath: core/models/organisation_role.py
from django.db import models
from django.conf import settings
from core.models.organisation_data import OrganisationData
from core.models.permission_profile import PermissionProfile  # Import at the top

class OrganisationRole(models.Model):
    ROLE_CHOICES = [
        ('SUPERADMIN', 'Super Admin'),
        ('ORGADMIN', 'Organisation Admin'),
        ('MANAGER', 'Manager'),
        ('EMPLOYEE', 'Employee'),
        ('VIEWER', 'Viewer'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='organisation_roles')
    organisation = models.ForeignKey(OrganisationData, on_delete=models.CASCADE, related_name='user_roles')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    assigned_at = models.DateTimeField(auto_now_add=True)

    permission_profile = models.ForeignKey(
        PermissionProfile, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='organisation_roles'
    )

    class Meta:
        unique_together = ('user', 'organisation', 'role')


   

   