# core/viewsets/permission.py
from rest_framework import viewsets
from core.models.permission_profile import Permission
from core.serializers.permissions_serializers import PermissionSerializer
from rest_framework.permissions import IsAuthenticated
from core.permissions.organisation_permissions import MinimumOrgAdmin

class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, MinimumOrgAdmin]

    def get_queryset(self):
        org_id = self.request.query_params.get('organisation')
        if org_id:
            return self.queryset.filter(profile__organisation_id=org_id)
        return self.queryset.none()  # Avoid exposing all perms
