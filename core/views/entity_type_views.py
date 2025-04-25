from rest_framework import viewsets, status
from core.models.entity_type import EntityType
from core.serializers.entity_type_serializers import EntityTypeSerializer
from rest_framework.response import Response

# Define a viewset for managing EntityType objects
class EntityTypeViewSet(viewsets.ModelViewSet):
    queryset = EntityType.objects.all()
    serializer_class = EntityTypeSerializer

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

            # Only superuser and instance admins can view entity types
            if admin_type_name in ["SUP", "INS"]:
                return EntityType.objects.all()
            else:
                return EntityType.objects.none()
        else:
            # Non-staff users cannot view entity types
            return EntityType.objects.none()