from rest_framework import viewsets, status
from core.models.admin_type import AdminType
from core.serializers.admin_type_serializers import AdminTypeSerializer
from rest_framework.response import Response

# Define a viewset for managing AdminType objects
class AdminTypeViewSet(viewsets.ModelViewSet):
    queryset = AdminType.objects.all()
    serializer_class = AdminTypeSerializer

    def create(self, request):
        # Handle admin type creation with validation and response
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        user = self.request.user
        
        # Check if user has admin access
        if user.is_staff and hasattr(user, 'admin_user'):
            admin_user = user.admin_user
            admin_type_name = admin_user.admin_type.name

            # Only superuser admins can view admin types
            if admin_type_name == "SUP":
                return AdminType.objects.all()
            else:
                return AdminType.objects.none()
        else:
            # Non-staff users cannot view admin types
            return AdminType.objects.none()