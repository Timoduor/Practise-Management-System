from rest_framework import serializers
from .base_serializers import SoftDeleteMixin
from .unit_serializers import UnitSerializer
from core.models.entity import Entity
from core.models.entity_type import EntityType
from core.serializers.entity_type_serializers import EntityTypeSerializer

# Serializer for Entity model with nested UnitSerializer for related units
class EntitySerializer(serializers.ModelSerializer, SoftDeleteMixin):
    units = UnitSerializer(many=True, read_only=True)  # Nested serializer for units within an entity
    entity_type =  serializers.PrimaryKeyRelatedField(queryset=EntityType.objects.all())
    entity_type_name = serializers.SerializerMethodField()  # Using SerializerMethodField for entity_type as name
    children = serializers.SerializerMethodField()
    parent_entity = serializers.PrimaryKeyRelatedField(queryset=Entity.objects.all(), required=False, allow_null=True)
    parent_entity_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Entity
        fields = [
            'id', 'name','entity_type','entity_type_name' , 'description', 'instance','children' , 'parent_entity' ,'parent_entity_name', 'is_deleted', 
            'created_at', 'updated_at', 'last_updated_by', 'created_by', "units"
        ]

    def get_children(self, obj):
        # Fetch child entities for the current entity
        children = Entity.objects.filter(parent_entity=obj)
        return EntitySerializer(children, many=True).data
    
    def get_entity_type_name(self, obj):
        # Retrieve the name of the entity type, if available
        return obj.entity_type.name if obj.entity_type else None
    
    def get_parent_entity_name(self,obj):
        return obj.parent_entity.name if obj.parent_entity else None

    def create(self, validated_data):
        user = self.context["request"]. user
        validated_data['instance'] = user.employee_user.instance 

        return super().create(validated_data)
