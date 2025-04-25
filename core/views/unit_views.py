from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from core.models.unit import Unit
from core.serializers.unit_serializers import UnitSerializer
from core.permissions import ReadOnlyUnlessSuperadmin
from rest_framework.response import Response

class UnitViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Units:
    - All authenticated users can read (GET) units based on their permissions.
    - Only superadmins can create/update/delete units.
    """
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    permission_classes = [IsAuthenticated, ReadOnlyUnlessSuperadmin]

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
        """
        Returns units based on user's permissions:
        - Superadmin: all units
        - Instance admin: units in their instance
        - Entity admin: units associated with their entity
        - Unit admin: their unit only
        - Regular users: units they belong to
        """
        user = self.request.user

        # Check if user has admin access
        if user.is_staff and hasattr(user, 'admin_user'):
            admin_user = user.admin_user
            admin_type_name = admin_user.admin_type.name
            jurisdiction = admin_user.jurisdiction

            if admin_type_name == "SUP":
                # Superuser admin - return all units
                return Unit.objects.all()
            elif admin_type_name == "INS":
                # Instance admin - return units in their instance
                instance = jurisdiction
                return Unit.objects.filter(instance=instance)
            elif admin_type_name == "ENT":
                # Entity admin - return units associated with their entity
                entity = jurisdiction
                return Unit.objects.filter(entities=entity)
            elif admin_type_name == "UNI":
                # Unit admin - return only their unit
                return Unit.objects.filter(id=jurisdiction.id)
        
        # Regular users - return units they belong to
        return Unit.objects.filter(members=user)
