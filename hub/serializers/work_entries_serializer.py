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
    supporting_document = serializers.FileField(required=False, allow_null=True)  # Added file upload
    duration = serializers.DurationField()  # Added duration field

    class Meta(SoftDeleteBaseSerializer.Meta):
        model = WorkEntries
        fields = [
            'work_entries_id', 'user', 'date', 'duration', 'description', 'supporting_document', 'customer',
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
        # Removed start_time/end_time validation

        project = data.get('project')
        phase = data.get('phase')
        task = data.get('task')

        if phase and phase.project != project:
            raise serializers.ValidationError("The selected phase does not belong to the selected project.")

        if task and task.phase != phase:
            raise serializers.ValidationError("The selected task does not belong to the selected phase.")

        return data

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
