from datetime import datetime
from rest_framework import serializers
from hub.models.project import Project
from hub.models.project_phase import ProjectPhase
from hub.models.task import Task
from hub.models.sales import Sales
from hub.models.sales_task import SalesTask
from hub.models.customer import Customer
from hub.models.task_type import TaskType
from hub.models.work_entries import WorkEntries

from .base_serializer import SoftDeleteBaseSerializer

class WorkEntriesSerializer(SoftDeleteBaseSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), required=False, allow_null=True)
    phase = serializers.PrimaryKeyRelatedField(queryset=ProjectPhase.objects.all(), required=False, allow_null=True)
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all(), required=False, allow_null=True)
    sale = serializers.PrimaryKeyRelatedField(queryset=Sales.objects.all(), required=False, allow_null=True)
    sales_task = serializers.PrimaryKeyRelatedField(queryset=SalesTask.objects.all(), required=False, allow_null=True)
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    task_type = serializers.PrimaryKeyRelatedField(queryset=TaskType.objects.all(), required=False, allow_null=True)

    class Meta(SoftDeleteBaseSerializer.Meta):
        model = WorkEntries
        fields = [
            'work_entries_id', 'user', 'date', 'start_time', 'end_time', 'description', 'customer', 
            'project', 'phase', 'task', 'sale', 'sales_task', 'task_type', 'is_deleted', 'created_at', 'updated_at'
        ] + SoftDeleteBaseSerializer.Meta.fields

        extra_kwargs = {
            'project': {'required': False, 'allow_null': True},
            'phase': {'required': False, 'allow_null': True},
            'task': {'required': False, 'allow_null': True},
            'sale': {'required': False, 'allow_null': True},
            'sales_task': {'required': False, 'allow_null': True},
            'task_type': {'required': False, 'allow_null': True},
        }

    def validate(self, data):
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        if start_time and end_time and start_time > end_time:
            raise serializers.ValidationError("End time must be after the start time.")

        project = data.get('project')
        phase = data.get('phase')
        task = data.get('task')

        if phase and phase.project != project:
            raise serializers.ValidationError("The selected phase does not belong to the selected project.")

        if task and task.phase != phase:
            raise serializers.ValidationError("The selected task does not belong to the selected phase.")

        return data

    def create(self, validated_data):
        start_time = validated_data.get('start_time')
        end_time = validated_data.get('end_time')

        if start_time and end_time:
            today = datetime.today().date()
            start_datetime = datetime.combine(today, start_time)
            end_datetime = datetime.combine(today, end_time)
            validated_data["duration"] = end_datetime - start_datetime
        else:
            validated_data["duration"] = None

        return super().create(validated_data)

    def update(self, instance, validated_data):
        start_time = validated_data.get('start_time', instance.start_time)
        end_time = validated_data.get('end_time', instance.end_time)

        if start_time and end_time:
            today = datetime.today().date()
            start_datetime = datetime.combine(today, start_time)
            end_datetime = datetime.combine(today, end_time)
            instance.duration = end_datetime - start_datetime
        else:
            instance.duration = None

        return super().update(instance, validated_data)
