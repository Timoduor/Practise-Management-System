from rest_framework import serializers
from .base_serializers import SoftDeleteMixin
from core.models.unit_type import UnitType


# Serializer for Unit model with SoftDeleteMixin
class UnitTypeSerializer(serializers.ModelSerializer, SoftDeleteMixin):
    class Meta:
        model = UnitType
        # Define fields for Unit model
        fields = [
            'id',  'unit_type', 'description', 'is_deleted', 'created_at', 
            'updated_at', 'last_updated_by', 'created_by'
        ]
