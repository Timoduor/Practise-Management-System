from rest_framework import serializers
from hub.models.task_status import TaskStatus

class TaskStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskStatus
        fields = ['id', 'name', 'description']
