from rest_framework import serializers
from .entity_serializers import EntitySerializer
from .base_serializers import SoftDeleteMixin
from core.models.instance import Instance

# Serializer for Instance model with nested EntitySerializer for related entities
class InstanceSerializer(serializers.ModelSerializer, SoftDeleteMixin):
    entities = EntitySerializer(many=True, read_only=True)  # Nested serializer for entities within an instance

    class Meta:
        model = Instance
        fields = [
            'id', 'name', 'code', 'industry', 'is_deleted', 'created_at', 
            'updated_at', 'last_updated_by', 'created_by', 'entities'
        ]
