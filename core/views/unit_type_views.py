from rest_framework import viewsets
from core.models.unit_type import UnitType
from core.serializers.unit_type_serializers import UnitTypeSerializer

# Define a viewset for managing Instance objects
class UnitTypeViewSet(viewsets.ModelViewSet):
    queryset = UnitType.objects.all()  # Retrieve all Instance objects
    serializer_class = UnitTypeSerializer  # Use InstanceSerializer for serialization

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return UnitType.objects.all()
        else:
            return UnitType.objects.none()