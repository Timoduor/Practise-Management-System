from rest_framework import serializers
from .base_serializers import BaseModelSerializer
from core.models.unit import Unit
from core.serializers.unit_type_serializers import UnitTypeSerializer
from core.models.unit_type import UnitType


class UnitSerializer(BaseModelSerializer):
    """
    Main serializer for Unit model with full details and nested relationships
    """
    # Nested relationships
    unit_type_details = UnitTypeSerializer(source='unit_type', read_only=True)
    
    # Related fields with validation
    unit_type = serializers.PrimaryKeyRelatedField(
        queryset=UnitType.objects.all(),
        required=False,
        allow_null=True
    )
    
    entity = serializers.PrimaryKeyRelatedField(
        queryset=Unit.objects.all(),
        required=False,
        allow_null=True
    )
    
    # Computed fields
    entity_name = serializers.CharField(source='entity.name', read_only=True)
    unit_type_name = serializers.CharField(source='unit_type.name', read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Unit
        fields = [
            'id',
            'name',
            'address',
            'unit_type',
            'unit_type_details',
            'unit_type_name',
            'entity',
            'entity_name',
            'full_name',
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

    def get_full_name(self, obj):
        """Generate full name with entity and unit name"""
        if obj.entity:
            return f"{obj.entity.entityName} - {obj.name}"
        return obj.name

    def validate_name(self, value):
        """
        Validate unit name:
        - Ensure proper length
        - Check uniqueness within same entity
        """
        value = value.strip()
        if len(value) > 15:
            raise serializers.ValidationError(
                "Unit name cannot exceed 15 characters."
            )
            
        # Check uniqueness within the same entity
        entity = self.initial_data.get('entity')
        if entity:
            existing = Unit.objects.filter(
                name=value,
                entity_id=entity
            ).exists()
            if existing and (not self.instance or self.instance.name != value):
                raise serializers.ValidationError(
                    "A unit with this name already exists in this entity."
                )
        return value

    def validate(self, data):
        """
        Validate unit data:
        - Check entity and unit type status
        """
        # Validate entity status if provided
        entity = data.get('entity')
        if entity and (entity.is_deleted or getattr(entity, 'Suspended', False)):
            raise serializers.ValidationError({
                'entity': 'Cannot assign unit to an inactive or suspended entity.'
            })
            
        # Validate unit type if provided
        unit_type = data.get('unit_type')
        if unit_type and unit_type.is_deleted:
            raise serializers.ValidationError({
                'unit_type': 'Cannot use an inactive unit type.'
            })
            
        return super().validate(data)

    def create(self, validated_data):
        """Create unit with proper user tracking"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
            validated_data['last_updated_by'] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update unit with proper user tracking"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['last_updated_by'] = request.user
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Enhance output with additional computed fields"""
        data = super().to_representation(instance)
        
        # Add status information
        data['status'] = 'Deleted' if instance.is_deleted else 'Active'
        
        # Add entity path if available
        if instance.entity:
            data['entity_path'] = instance.entity.entityName
            if hasattr(instance.entity, 'parent'):
                parent = instance.entity.parent
                while parent:
                    data['entity_path'] = f"{parent.name} > {data['entity_path']}"
                    parent = parent.parent
                    
        return data


class UnitListSerializer(UnitSerializer):
    """Simplified serializer for list views"""
    class Meta(UnitSerializer.Meta):
        fields = [
            'id',
            'name',
            'unit_type_name',
            'entity_name',
            'status',
        ]


class UnitSimpleSerializer(serializers.ModelSerializer):
    """Minimal serializer for nested relationships"""
    class Meta:
        model = Unit
        fields = [
            'id',
            'name',
        ]