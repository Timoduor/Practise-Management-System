from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from .common_viewset import CommonViewSet
from hub.serializers.task_serializer import TaskSerializer
from django.utils.timezone import now
from hub.models.task import Task


class TaskViewSet(CommonViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            match user.admin_user.admin_type.name:
                case "SUP":
                  return Task.objects.all()
                case "INS":
                  return Task.objects.filter(entity__instance = user.employee_user.instance)
                case "ENT":
                    return Task.objects.filter(project__entity= user.employee_user.entity)  
                case "UNI":
                    return Task.objects.filter(project__unit= user.employee_user.unit)

        return Task.objects.filter(project = user.employee_user.project_members)

