from rest_framework import serializers
from .base_serializer import SoftDeleteBaseSerializer
from hub.models.project import Project
from hub.models.project_phase import ProjectPhase
from hub.models.task import Task
from hub.models.sales import Sales
from hub.models.sales_task import SalesTask
from hub.models.customer import Customer
from hub.models.expense import Expense


class ExpenseSerializer(SoftDeleteBaseSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), required=False, allow_null=True)
    phase = serializers.PrimaryKeyRelatedField(queryset=ProjectPhase.objects.all(), allow_null=True)
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all(), allow_null=True)
    sale = serializers.PrimaryKeyRelatedField(queryset=Sales.objects.all(), allow_null=True)
    sales_task = serializers.PrimaryKeyRelatedField(queryset=SalesTask.objects.all(), allow_null=True)
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(), allow_null=True)

    duration = serializers.DurationField(required=False, allow_null=True)  # Added duration field

    class Meta(SoftDeleteBaseSerializer.Meta):
        model = Expense
        fields = ['expense_id', 'user', 'customer', 'project', 'phase', 'task', 'sale', 'sales_task', 
                  'date', 'value', 'description', 'duration', 'is_deleted', 'created_at', 'updated_at'] + SoftDeleteBaseSerializer.Meta.fields

    def validate(self, data):
        project = data.get('project')
        phase = data.get('phase')
        task = data.get('task')

        if phase and phase.project != project:
            raise serializers.ValidationError("The selected phase does not belong to the selected project.")

        if task and task.phase != phase:
            raise serializers.ValidationError("The selected task does not belong to the selected phase.")

        return data
