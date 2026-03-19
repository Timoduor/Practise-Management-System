from rest_framework import serializers
from hub.models.task_type import TaskType

class TaskTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskType
        fields = ['id', 'name', 'description']
