from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from hub.models.task_type import TaskType
from hub.serializers.task_type_serializer import TaskTypeSerializer

class TaskTypeViewSet(viewsets.ModelViewSet):
    """
    Any authenticated user can CRUD TaskTypes.
    """
    queryset = TaskType.objects.all()
    serializer_class = TaskTypeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return TaskType.objects.all()
        return TaskType.objects.none()
