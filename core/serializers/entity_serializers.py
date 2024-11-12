from rest_framework import serializers
from .base_serializers import SoftDeleteMixin
from .unit_serializers import UnitSerializer
from core.models.entity import Entity

# Serializer for Entity model with nested UnitSerializer for related units
class EntitySerializer(serializers.ModelSerializer, SoftDeleteMixin):
    units = UnitSerializer(many=True, read_only=True)  # Nested serializer for units within an entity
    children = serializers.SerializerMethodField()
    class Meta:
        model = Entity
        fields = [
            'id', 'name', 'entity_type', 'description', 'instance','children' , 'parent_entity', 'is_deleted', 
            'created_at', 'updated_at', 'last_updated_by', 'created_by', "units"
        ]

    def get_children(self, obj):
        # Fetch child entities for the current entity
        children = Entity.objects.filter(parent_entity=obj)
        return EntitySerializer(children, many=True).data
    

    def create(self, validated_data):
        user = self.context["request"]. user
        validated_data['instance'] = user.employee_user.instance 

        return super().create(validated_data)
