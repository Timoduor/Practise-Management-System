from rest_framework import viewsets, status
from core.models.unit_type import UnitType
from core.serializers.unit_type_serializers import UnitTypeSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions.hierachial_permissions import HierarchicalOrgPermission
from core.models.organisation_role import OrganisationRole
from core.utils.permissions import get_organisation_id_from_request

# Define a viewset for managing UnitType objects
class UnitTypeViewSet(viewsets.ModelViewSet):
    queryset = UnitType.objects.all()
    serializer_class = UnitTypeSerializer
    permission_classes = [IsAuthenticated, HierarchicalOrgPermission]

    def get_object(self):
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj


    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Set created_by and last_updated_by to current user
        serializer.validated_data['created_by'] = request.user
        serializer.validated_data['last_updated_by'] = request.user
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # Set last_updated_by to current user
        serializer.validated_data['last_updated_by'] = request.user

        self.perform_update(serializer)
        return Response(serializer.data)

    def get_queryset(self):
        user = self.request.user
        
        # Check if user has admin access
        if user.is_staff and hasattr(user, 'admin_user'):
            admin_user = user.admin_user
            admin_type_name = admin_user.admin_type.name

            # Only superuser and instance admins can view unit types
            if admin_type_name in ["SUP", "INS"]:
                return UnitType.objects.all()
            else:
                return UnitType.objects.none()
        else:
            # Non-staff users cannot view unit types
            return UnitType.objects.none()
        

   