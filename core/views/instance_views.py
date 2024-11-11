from rest_framework import viewsets
from core.models.instance import Instance
from core.serializers.instance_serializers import InstanceSerializer

# Define a viewset for managing Instance objects
class InstanceViewSet(viewsets.ModelViewSet):
    queryset = Instance.objects.all()  # Retrieve all Instance objects
    serializer_class = InstanceSerializer  # Use InstanceSerializer for serialization

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Instance.objects.all()
        else:
            return Instance.objects.filter(instance= user.employee_user.instance)