from rest_framework import serializers
from core.models.entity import Entity
from core.models.unit import Unit
from hub.models.customer import Customer
from .project_serializer import ProjectSerializer
from .sales_serializer import SalesSerializer
from .contact_serializer import ContactSerializer
from .base_serializer import SoftDeleteBaseSerializer


class CustomerSerializer(SoftDeleteBaseSerializer):
    contacts = ContactSerializer(many=True, read_only=True)
    
    sales = SalesSerializer(many=True, read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)

    entity = serializers.PrimaryKeyRelatedField(queryset=Entity.objects.all(), required=False, allow_null=True)
    unit = serializers.PrimaryKeyRelatedField(queryset=Unit.objects.all(), required=False, allow_null=True)

    class Meta(SoftDeleteBaseSerializer.Meta):
        model = Customer
        fields = ['customer_id', 'customer_name', 'customer_email', 'customer_phone', 'customer_address', 'entity', 'unit', 'is_deleted', 'created_at', 'updated_at', 'contacts', 'sales', 'projects'] + SoftDeleteBaseSerializer.Meta.fields

    def validate(self, data):
        entity = data.get('entity')
        unit = data.get('unit')

        if unit and entity:
            if unit.entity != entity:
                raise serializers.ValidationError({
                    'unit': 'The selected unit must belong to the selected entity.'
                })
        
        return data
    

