from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from hub.models.task_status import TaskStatus
from hub.serializers.task_status_serializer import TaskStatusSerializer


class TaskStatusViewSet(viewsets.ModelViewSet):
    queryset = TaskStatus.objects.all()
    serializer_class = TaskStatusSerializer
    permission_classes = [IsAuthenticated]
