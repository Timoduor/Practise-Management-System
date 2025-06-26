# core/views/organisation_views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from core.permissions.hierachial_permissions import HierarchicalOrgPermission
from core.models.organisation_role import OrganisationRole
from core.serializers.organisation_role_serializer import OrganisationRoleSerializer
from core.permissions.hierachial_permissions import HierarchicalOrgPermission
from core.models.organisation_data import OrganisationData
from core.serializers.organisation_data_serializers import OrganisationDataSerializer
from core.permissions.organisation_permissions import MinimumManager
from core.permissions.modular_permissions import CanInviteUsers


class OrganisationRoleViewSet(viewsets.ModelViewSet):
    queryset = OrganisationRole.objects.all()
    serializer_class = OrganisationRoleSerializer
    permission_classes = [
        IsAuthenticated,
        HierarchicalOrgPermission,  # Keep if needed
        MinimumManager,             # Role-based minimum access
        CanInviteUsers              # Feature-level permission
    ]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return OrganisationRole.objects.none()
        return super().get_queryset()  

        
class OrganisationDataViewSet(viewsets.ModelViewSet):
    queryset = OrganisationData.objects.all()
    serializer_class = OrganisationDataSerializer
    permission_classes = [IsAuthenticated, HierarchicalOrgPermission]

