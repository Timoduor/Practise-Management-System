from django.db import models
from core.models.organisation_data import OrganisationData

class PermissionProfile(models.Model):
    organisation = models.ForeignKey(
        OrganisationData,
        on_delete=models.CASCADE,
        related_name='permission_profiles',
        null=True,
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ('organisation', 'name')

    def __str__(self):
        return self.name


class Permission(models.Model):
    profile = models.ForeignKey(PermissionProfile, related_name='permissions', on_delete=models.CASCADE)
    code = models.CharField(max_length=100)  # e.g. "can_invite_users"
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ('profile', 'code')

    def __str__(self):
        return f"{self.profile.name} - {self.code}"


