from rest_framework import serializers
from .base_serializers import SoftDeleteMixin
from core.models.admin_type import AdminType


# Serializer for Unit model with SoftDeleteMixin
class AdminTypeSerializer(serializers.ModelSerializer, SoftDeleteMixin):
    class Meta:
        model = AdminType
        # Define fields for Entity Type model
        fields = [
            'id',  'name', 'description', 'is_deleted', 'created_at', 
            'updated_at', 'last_updated_by', 'created_by'
        ]
