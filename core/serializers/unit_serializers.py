from rest_framework import serializers
from .base_serializers import SoftDeleteMixin
from core.models.unit import Unit


# Serializer for Unit model with SoftDeleteMixin
class UnitSerializer(serializers.ModelSerializer, SoftDeleteMixin):
    class Meta:
        model = Unit
        # Define fields for Unit model
        fields = [
            'id', 'name', 'unit_type', 'address', 'entity', 'is_deleted', 'created_at', 
            'updated_at', 'last_updated_by', 'created_by'
        ]
