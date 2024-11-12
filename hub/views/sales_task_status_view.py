from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from hub.models.sales_task_status import SalesTaskStatus
from hub.serializers.sales_task_status_serializer import SalesTaskStatusSerializer

class SalesTaskStatusViewSet(viewsets.ModelViewSet):
    queryset = SalesTaskStatus.objects.all()
    serializer_class = SalesTaskStatusSerializer
    permission_classes = [IsAuthenticated]
