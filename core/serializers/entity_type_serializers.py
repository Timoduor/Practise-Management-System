from rest_framework import serializers
from .base_serializers import SoftDeleteMixin
from core.models.entity_type import EntityType


# Serializer for Unit model with SoftDeleteMixin
class EntityTypeSerializer(serializers.ModelSerializer, SoftDeleteMixin):
    class Meta:
        model = EntityType
        # Define fields for Entity Type model
        fields = [
            'id',  'name', 'description', 'is_deleted', 'created_at', 
            'updated_at', 'last_updated_by', 'created_by'
        ]
