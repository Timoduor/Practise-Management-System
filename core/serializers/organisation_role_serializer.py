from rest_framework import serializers
from core.models.organisation_role import OrganisationRole

class OrganisationRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganisationRole
        fields = [
            'id',
            'user',
            'organisation',
            'role',
            'is_active',
            'assigned_at',
            'permission_profile'
        ]