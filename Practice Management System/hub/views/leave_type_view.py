from rest_framework import viewsets
from hub.models.leave_type import LeaveType
from hub.serializers.leave_type_serializer import LeaveTypeSerializer

class LeaveTypeViewSet(viewsets.ModelViewSet):
    """
    Any authenticated user can CRUD LeaveTypes.
    """
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    # If you need only authenticated access, add:
    # permission_classes = [IsAuthenticated]
