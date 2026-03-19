from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from .common_viewset import CommonViewSet
from hub.serializers.task_serializer import TaskSerializer
from django.utils.timezone import now
from hub.models.task import Task

class TaskViewSet(CommonViewSet):
    """
    Any authenticated user can CRUD Tasks.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Task.objects.all()
        return Task.objects.none()
