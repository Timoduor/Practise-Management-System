from rest_framework import serializers
from core.models import User  
from .models import Customer, Contact, Sales

class CustomerSerializer(serializers.ModelSerializer):
    contacts = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    sales = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Customer
        fields = ['customer_id', 'customer_name', 'customer_email', 'customer_phone', 'customer_address', 'entity', 'unit', 'is_deleted', 'created_at', 'updated_at', 'contacts', 'sales']

    def validate(self, data):
        entity = data.get('entity')
        unit = data.get('unit')

        # Check if the unit belongs to the entity
        if unit and entity:
            if unit.entity != entity:
                raise serializers.ValidationError({
                    'unit': 'The selected unit must belong to the selected entity.'
                })
        
        return data


class ContactSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())

    class Meta:
        model = Contact
        fields = ['contact_id', 'contact_name', 'contact_email', 'contact_phone', 'contact_address', 'role', 'customer', 'is_deleted', 'created_at', 'updated_at']


class SalesSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    project_manager = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

    class Meta:
        model = Sales
        fields = [
            'sales_id', 'sales_name', 'sales_description', 'project_value', 
            'expected_order_date', 'sales_status', 'customer', 'project_manager', 
            'created_by', 'entity', 'unit', 'is_deleted', 'created_at', 'updated_at'
        ]

    def validate(self, data):
        project_manager = data.get('project_manager')
        entity = data.get('entity')

        # Check if the project manager belongs to the same instance as the sale's entity
        if project_manager and entity:
            if project_manager.employee_entity != entity:
                raise serializers.ValidationError({
                    'project_manager': 'The selected project manager must belong to the same entity as the sale.'
                })

        return data
