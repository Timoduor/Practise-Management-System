from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from hub.models.task_type import TaskType
from hub.serializers.task_type_serializer import TaskTypeSerializer


class TaskTypeViewSet(viewsets.ModelViewSet):
    queryset = TaskType.objects.all()
    serializer_class = TaskTypeSerializer
    permission_classes = [IsAuthenticated]
