from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from hub.models.sales_task_type import SalesTaskType
from hub.serializers.sales_task_type_serializer import SalesTaskTypeSerializer

class SalesTaskTypeViewSet(viewsets.ModelViewSet):
    queryset = SalesTaskType.objects.all()
    serializer_class = SalesTaskTypeSerializer
    permission_classes = [IsAuthenticated]
