from rest_framework import viewsets
from core.models.admin_type import AdminType
from core.serializers.admin_type_serializers import AdminTypeSerializer

# Define a viewset for managing Instance objects
class AdminTypeViewSet(viewsets.ModelViewSet):
    queryset = AdminType.objects.all()  # Retrieve all AdminType objects
    serializer_class = AdminTypeSerializer  # Use AdminTypeSerializer for serialization

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return AdminType.objects.all()
        else:
            return AdminType.objects.none()