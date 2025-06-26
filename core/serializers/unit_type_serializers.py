from rest_framework import serializers
from .base_serializers import BaseModelSerializer
from core.models.unit_type import UnitType
from core.models.organisation_role import OrganisationRole
from core.permissions.base_permissions import ROLE_HIERARCHY

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
    
    
     
    def get_fields(self):
        fields = super().get_fields()  # Get all default fields from the serializer
        request = self.context.get('request')  # Get the request object passed into the serializer
        user = getattr(request, 'user', None)  # Get the user making the request

        if not user or not user.is_authenticated:
            hide_fields = True  # If no user or user is anonymous, hide sensitive fields
        elif user.is_superuser:
            hide_fields = False  # Django superusers see everything
        else:
            # Get organisation ID from request or object (fall back based on how you're accessing it)
            org_id = (
                request.data.get('organisation') or
                request.query_params.get('organisation') or
                getattr(getattr(self.instance, 'organisation', None), 'id', None)
            )

            if not org_id:
                hide_fields = True  # If we don't know which organisation, hide
            else:
                # Get user's roles in that organisation
                user_roles = OrganisationRole.objects.filter(
                    user=user,
                    organisation_id=org_id,
                    is_active=True
                ).values_list('role', flat=True)

                # Check if user has ORGADMIN or higher access
                hide_fields = all(
                    ROLE_HIERARCHY.get(role, -1) < ROLE_HIERARCHY['ORGADMIN']
                    for role in user_roles
                )

        # Hide sensitive fields if the user is not authorised
        if hide_fields:
            for field_name in ['LastUpdatedByID', 'DateAdded', 'LastUpdate']:
                fields.pop(field_name, None)

        return fields


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