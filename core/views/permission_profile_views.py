# core/views/permission_profile_views.py
from rest_framework import viewsets, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from core.models.permission_profile import PermissionProfile
from core.serializers.permission_profile_serializer import PermissionProfileSerializer


class PermissionProfileViewSet(viewsets.ModelViewSet):
    serializer_class = PermissionProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            return PermissionProfile.objects.none()
        org_ids = user.organisation_roles.values_list('organisation_id', flat=True)
        return PermissionProfile.objects.filter(organisation_id__in=org_ids)

    def perform_create(self, serializer):
        user = self.request.user
        organisation_id = self.request.data.get('organisation_id')

        if not organisation_id:
            raise serializers.ValidationError("organisation_id is required")

        if not user.organisation_roles.filter(organisation_id=organisation_id).exists():
            raise PermissionDenied("You cannot create profiles for this organisation.")

        serializer.save(organisation_id=organisation_id)

