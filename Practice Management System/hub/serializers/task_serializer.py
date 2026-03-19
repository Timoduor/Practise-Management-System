from rest_framework import serializers
from .base_serializer import SoftDeleteBaseSerializer
from hub.models.project import  Project
from hub.models.task import Task
from hub.models.task_status import TaskStatus
from core.models.employee import Employee
from core.serializers import EmployeeSerializer
from .task_status_serializer import TaskStatusSerializer


class TaskSerializer(SoftDeleteBaseSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    assigned_to = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), required=False)
    assigned_to_details = EmployeeSerializer(read_only=True)

    # Use PrimaryKeyRelatedField for setting task_status, nested serializer for read
    task_status = serializers.PrimaryKeyRelatedField(queryset=TaskStatus.objects.all())
    task_status_display = serializers.SerializerMethodField()

    class Meta(SoftDeleteBaseSerializer.Meta):
        model = Task
        fields = [
            'task_id', 'task_name', 'project', 'phase', 'assigned_to', 'assigned_to_details', 
            'start_date', 'due_date', 'task_description', 'task_status', 'task_status_display', 
            'is_deleted', 'created_at', 'updated_at'
        ] + SoftDeleteBaseSerializer.Meta.fields

    def validate(self, data):
        start_date = data.get('start_date')
        due_date = data.get('due_date')

        # Validate start and due dates
        if start_date and due_date and start_date > due_date:
            raise serializers.ValidationError("Due date must be after the start date.")

        project = data.get('project')
        phase = data.get('phase')

        # Validate that phase belongs to the project
        if phase and phase.project != project:
            raise serializers.ValidationError("The phase must belong to the selected project.")

        return data
    
    def get_task_status_display(self,obj):
        return obj.task_status.name if obj.task_status else None
