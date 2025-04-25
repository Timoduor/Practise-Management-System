from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from core.models.instance import Instance
from core.serializers.instance_serializers import InstanceSerializer
from core.permissions import ReadOnlyUnlessSuperadmin
from rest_framework.response import Response

class InstanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Instances:
    - All authenticated users can read (GET) all instances.
    - Only superadmins can create/update/delete instances.
    """
    queryset = Instance.objects.all()
    serializer_class = InstanceSerializer
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
        Returns all instances for all authenticated users.
        """
        user = self.request.user

        # Allow access only if the user is authenticated
        if user.is_authenticated:  
            return Instance.objects.all()  # All users can view all instances

        # If the user isn't authenticated, return an empty queryset (should not happen)
        return Instance.objects.none()
