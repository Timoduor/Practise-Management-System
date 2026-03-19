from rest_framework import serializers
from hub.models.sales import Sales
from hub.models.sales_status import SalesStatus
from core.models.user import User
from core.models.employee import Employee
from hub.models.customer import Customer
from .base_serializer import SoftDeleteBaseSerializer
from .sales_task_serializer import SalesTaskSerializer
from .sales_status_serializer import SalesStatusSerializer
from core.serializers.employee_serializers import EmployeeSerializer


class SalesSerializer(SoftDeleteBaseSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    project_manager = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), required=False)
    created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    sales_tasks = SalesTaskSerializer(many=True, read_only=True)
    
    members = EmployeeSerializer(many=True, read_only=True)
    member_ids = serializers.PrimaryKeyRelatedField(
        many=True,  queryset=Employee.objects.all(), source='members', required=False
    )

    # Use PrimaryKeyRelatedField for setting, SalesTypeSerializer for display
    sales_status = serializers.PrimaryKeyRelatedField(queryset=SalesStatus.objects.all())  # For write operations
    sales_status_display = serializers.SerializerMethodField()   # For read operations

    class Meta(SoftDeleteBaseSerializer.Meta):
        model = Sales
        fields = [
            'sales_id', 'sales_name', 'sales_description', 'project_value', 
            'expected_order_date', 'sales_status', 'sales_status_display', 'sales_tasks',
            'customer', 'project_manager','members', 'member_ids', 'created_by', 'instance', 'entity', 'unit', 
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
    
    def create(self, validated_data):
        members = validated_data.pop('members', [])
        sale = Sales.objects.create(**validated_data)
        sale.members.set(members)  # Add members to the sale
        return sale

    def update(self, instance, validated_data):
        members = validated_data.pop('members', [])
        instance = super().update(instance, validated_data)
        instance.members.set(members)  # Update the members of the sale
        return instance




    def get_sales_status_display(self, obj):
        return obj.sales_status.name if obj.sales_status else None
    