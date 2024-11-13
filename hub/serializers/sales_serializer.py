from rest_framework import serializers
from hub.models.sales import Sales
from hub.models.sales_status import SalesStatus
from core.models.user import User
from core.models.employee import Employee
from hub.models.customer import Customer
from .base_serializer import SoftDeleteBaseSerializer
from .sales_task_serializer import SalesTaskSerializer
from .sales_status_serializer import SalesStatusSerializer


class SalesSerializer(SoftDeleteBaseSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    project_manager = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), required=False)
    created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    sales_tasks = SalesTaskSerializer(many=True, read_only=True)
    
    # Use PrimaryKeyRelatedField for setting, SalesTypeSerializer for display
    sales_status = serializers.PrimaryKeyRelatedField(queryset=SalesStatus.objects.all())  # For write operations
    sales_status_display = SalesStatusSerializer(source='sales_status', read_only=True)    # For read operations

    class Meta(SoftDeleteBaseSerializer.Meta):
        model = Sales
        fields = [
            'sales_id', 'sales_name', 'sales_description', 'project_value', 
            'expected_order_date', 'sales_status', 'sales_status_display', 'sales_tasks',
            'customer', 'project_manager', 'created_by', 'entity', 'unit', 
            'is_deleted', 'created_at', 'updated_at'
        ] + SoftDeleteBaseSerializer.Meta.fields

    def validate(self, data):
        project_manager = data.get('project_manager')
        entity = data.get('entity')

        # Check if the project manager belongs to the same instance as the sale's entity
        if project_manager and entity:
            if project_manager.entity != entity:
                raise serializers.ValidationError({
                    'project_manager': 'The selected project manager must belong to the same entity as the sale.'
                })

        return data
