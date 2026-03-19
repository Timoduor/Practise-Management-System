from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from hub.models.sales_task_type import SalesTaskType
from hub.serializers.sales_task_type_serializer import SalesTaskTypeSerializer

class SalesTaskTypeViewSet(viewsets.ModelViewSet):
    queryset = SalesTaskType.objects.all()
    serializer_class = SalesTaskTypeSerializer
    permission_classes = [IsAuthenticated]
    # Since we want full access for all authenticated users,
    # we can leave get_queryset() as default or override:
    #
    # def get_queryset(self):
    #     if self.request.user.is_authenticated:
    #         return SalesTaskType.objects.all()
    #     return SalesTaskType.objects.none()
