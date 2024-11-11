from rest_framework import viewsets
from core.models.entity_type import EntityType
from core.serializers.entity_type_serializers import EntityTypeSerializer

# Define a viewset for managing Instance objects
class EntityTypeViewSet(viewsets.ModelViewSet):
    queryset = EntityType.objects.all()  # Retrieve all Instance objects
    serializer_class = EntityTypeSerializer  # Use InstanceSerializer for serialization

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return EntityType.objects.all()
        else:
            return EntityType.objects.none()