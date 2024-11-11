from rest_framework import serializers
from hub.models import Customer
from .contact_serializer import ContactSerializer
from .project_serializer import ProjectSerializer
from .sales_serializer import SalesSerializer


class CustomerSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(many=True, read_only=True)
    
    sales = SalesSerializer(many=True, read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)

    class Meta:
        model = Customer
        fields = ['customer_id', 'customer_name', 'customer_email', 'customer_phone', 'customer_address', 'entity', 'unit', 'is_deleted', 'created_at', 'updated_at', 'contacts', 'sales', 'projects']

    def validate(self, data):
        entity = data.get('entity')
        unit = data.get('unit')

        if unit and entity:
            if unit.entity != entity:
                raise serializers.ValidationError({
                    'unit': 'The selected unit must belong to the selected entity.'
                })
        
        return data

