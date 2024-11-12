from rest_framework import viewsets
from hub.models.leave_type import LeaveType
from hub.serializers.leave_type_serializer import LeaveTypeSerializer

class LeaveTypeViewSet(viewsets.ModelViewSet):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer

