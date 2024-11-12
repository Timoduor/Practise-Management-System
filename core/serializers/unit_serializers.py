from rest_framework import serializers
from .base_serializers import SoftDeleteMixin
from core.models.unit import Unit
from core.serializers.unit_type_serializers import UnitTypeSerializer


# Serializer for Unit model with SoftDeleteMixin
class UnitSerializer(serializers.ModelSerializer, SoftDeleteMixin):
    unit_type = serializers.SerializerMethodField()  # Using SerializerMethodField for entity_type as name

    class Meta:
        model = Unit
        # Define fields for Unit model
        fields = [
            'id', 'name', 'unit_type', 'address', 'entity', 'is_deleted', 'created_at', 
            'updated_at', 'last_updated_by', 'created_by'
        ]

    def get_unit_type(self,obj):
        return obj.unit_type.name if obj.unit_type else None
