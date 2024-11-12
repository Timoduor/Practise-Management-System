from rest_framework import serializers
from .base_serializer import SoftDeleteBaseSerializer
from .sales_task_type_serializer import SalesTaskTypeSerializer
from hub.models.sales import Sales
from hub.models.sales_task import SalesTask
from hub.models.sales_task_status import SalesTaskStatus
from hub.models.sales_task_type import SalesTaskType
from core.models.employee import Employee
from core.serializers.employee_serializers import EmployeeSerializer
from .sales_task_status_serializer import SalesTaskStatusSerializer


class SalesTaskSerializer(SoftDeleteBaseSerializer):
    sale = serializers.PrimaryKeyRelatedField(queryset=Sales.objects.all())
    assigned_to = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all())
    assigned_to_details = EmployeeSerializer(read_only=True)
    
    # Use PrimaryKeyRelatedField for setting task_type and task_status, nested serializers for read
    task_type = serializers.PrimaryKeyRelatedField(queryset=SalesTaskType.objects.all())
    task_type_display = SalesTaskTypeSerializer(source='task_type', read_only=True)
    task_status = serializers.PrimaryKeyRelatedField(queryset=SalesTaskStatus.objects.all())
    task_status_display = SalesTaskStatusSerializer(source='task_status', read_only=True)

    class Meta(SoftDeleteBaseSerializer.Meta):
        model = SalesTask
        fields = [
            'sales_task_id', 'task_name', 'task_type', 'task_type_display', 
            'task_status', 'task_status_display', 'assigned_to', 'assigned_to_details', 
            'sale', 'date', 'task_description', 'is_deleted', 'created_at', 'updated_at'
        ] + SoftDeleteBaseSerializer.Meta.fields
