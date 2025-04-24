from rest_framework import serializers
from .base_serializers import BaseModelSerializer
from core.models.unit_type import UnitType


class UnitTypeSerializer(BaseModelSerializer):
    """
    Main serializer for UnitType model with full details and validation
    """
    # Additional computed fields
    units_count = serializers.SerializerMethodField()
    active_units_count = serializers.SerializerMethodField()

    class Meta:
        model = UnitType
        fields = [
            'id',
            'name',
            'description',
            'units_count',
            'active_units_count',
            'is_deleted',
            'created_at',
            'updated_at',
            'created_by',
            'last_updated_by',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'created_by',
            'last_updated_by',
        ]

    def get_units_count(self, obj):
        """Get total number of units of this type"""
        return obj.unit_set.count()

    def get_active_units_count(self, obj):
        """Get number of active units of this type"""
        return obj.unit_set.filter(is_deleted=False).count()

    def validate_name(self, value):
        """
        Validate unit type name:
        - Ensure proper length
        - Check uniqueness
        - Proper formatting
        """
        value = value.strip()
        if len(value) > 40:
            raise serializers.ValidationError(
                "Unit type name cannot exceed 40 characters."
            )

        # Check uniqueness case-insensitive
        if UnitType.objects.filter(name__iexact=value).exists():
            if not self.instance or self.instance.name.lower() != value.lower():
                raise serializers.ValidationError(
                    "A unit type with this name already exists."
                )

        return value

    def validate_description(self, value):
        """
        Validate unit type description:
        - Ensure not empty
        - Proper formatting
        """
        if not value or not value.strip():
            raise serializers.ValidationError(
                "Description cannot be empty."
            )
        return value.strip()

    def create(self, validated_data):
        """Create unit type with proper user tracking"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
            validated_data['last_updated_by'] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update unit type with proper user tracking"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['last_updated_by'] = request.user
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Enhance output with additional computed fields"""
        data = super().to_representation(instance)
        
        # Add status information
        data['status'] = 'Deleted' if instance.is_deleted else 'Active'
        
        # Add usage statistics
        units = instance.unit_set.all()
        data['statistics'] = {
            'total_units': units.count(),
            'active_units': units.filter(is_deleted=False).count(),
            'deleted_units': units.filter(is_deleted=True).count(),
        }
        
        return data


class UnitTypeListSerializer(UnitTypeSerializer):
    """Simplified serializer for list views"""
    class Meta(UnitTypeSerializer.Meta):
        fields = [
            'id',
            'name',
            'active_units_count',
            'status',
        ]


class UnitTypeSimpleSerializer(serializers.ModelSerializer):
    """Minimal serializer for nested relationships"""
    class Meta:
        model = UnitType
        fields = [
            'id',
            'name',
        ]