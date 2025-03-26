from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from core.models.instance import Instance
from core.serializers.instance_serializers import InstanceSerializer
from core.permissions import ReadOnlyUnlessSuperadmin 
class InstanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Instances:
    - All authenticated users can read (GET) all instances.
    - Only superadmins can create/update/delete instances.
    """
    queryset = Instance.objects.all()
    serializer_class = InstanceSerializer
    permission_classes = [IsAuthenticated, ReadOnlyUnlessSuperadmin]  # <- Ensure IsAuthenticated is here

    def get_queryset(self):
        """
        Returns all instances for all authenticated users.
        """
        user = self.request.user

        # Allow access only if the user is authenticated
        if user.is_authenticated:  
            return Instance.objects.all()  # All users can view all instances

        # If the user isn't authenticated, return an empty queryset (should not happen)
        return Instance.objects.none()  
