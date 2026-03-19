from rest_framework.permissions import IsAuthenticated
from .common_viewset import CommonViewSet
from hub.serializers.sales_task_serializer import SalesTaskSerializer
from hub.models.sales_task import SalesTask


class SalesTaskViewSet(CommonViewSet):
    queryset = SalesTask.objects.all()
    serializer_class = SalesTaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Any authenticated user sees all sales tasks
        user = self.request.user
        if user.is_authenticated:
            return SalesTask.objects.all()
        return SalesTask.objects.none()
