from rest_framework import serializers
from .base_serializers import SoftDeleteMixin
from core.models.unit import Unit
from core.serializers.unit_type_serializers import UnitTypeSerializer
from core.models.unit_type import UnitType


# Serializer for Unit model with SoftDeleteMixin
class UnitSerializer(serializers.ModelSerializer, SoftDeleteMixin):
    unit_type_name = serializers.SerializerMethodField()  # Using SerializerMethodField for entity_type as name
    unit_type = serializers.PrimaryKeyRelatedField(queryset=UnitType.objects.all(), required=False)

    class Meta:
        model = Unit
        # Define fields for Unit model
        fields = [
            'id', 'name', 'unit_type','unit_type_name' ,'address', 'entity', 'is_deleted', 'created_at', 
            'updated_at', 'last_updated_by', 'created_by'
        ]

    def get_unit_type_name(self,obj):
        return obj.unit_type.name if obj.unit_type else None
