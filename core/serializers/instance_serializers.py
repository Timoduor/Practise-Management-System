from rest_framework import serializers
from .entity_serializers import EntitySerializer
from .base_serializers import BaseModelSerializer
from core.models.instance import Instance
from core.models.industry_sector import IndustrySector
from core.models.organisation_role import OrganisationRole
from core.permissions.base_permissions import ROLE_HIERARCHY

class InstanceSerializer(BaseModelSerializer):
    """
    Serializer for Instance model with nested relationships and proper tracking
    """
    # Nested relationships
    entities = EntitySerializer(many=True, read_only=True)
    
    # Related fields
    industrySector = serializers.PrimaryKeyRelatedField(
        queryset=IndustrySector.objects.all(),
        required=True
    )
    
    # Additional fields
    industry_title = serializers.CharField(read_only=True)
    entities_count = serializers.SerializerMethodField()

    class Meta:
        model = Instance
        fields = [
            'instanceID',
            'DateAdded',
            'instanceName',
            'industrySector',
            'industry_title',
            'Lapsed',
            'Suspended',
            'entities',
            'entities_count',
            'is_deleted',
            'created_at',
            'updated_at',
            'created_by',
            'last_updated_by',
        ]
        read_only_fields = [
            'instanceID',
            'DateAdded',
            'created_at',
            'updated_at',
            'created_by',
            'last_updated_by',
        ]

    def get_entities_count(self, obj):
        """Get count of entities in this instance"""
        return obj.entities.count()

    def validate_instanceName(self, value):
        """
        Validate instance name:
        - Ensure it's unique
        - Proper formatting
        """
        value = value.strip()
        
        # Check uniqueness
        if Instance.objects.filter(instanceName=value).exists():
            if not self.instance or self.instance.instanceName != value:
                raise serializers.ValidationError(
                    "An instance with this name already exists."
                )
        return value

    def validate(self, data):
        """
        Validate instance data:
        - Check industry sector status
        """
        industry_sector = data.get('industrySector')
        if industry_sector and industry_sector.Suspended == 'Y':
            raise serializers.ValidationError({
                'industrySector': 'Cannot use a suspended industry sector.'
            })
        return super().validate(data)

    def create(self, validated_data):
        """Create instance with proper user tracking"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
            validated_data['last_updated_by'] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update instance with proper user tracking"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['last_updated_by'] = request.user
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Add additional computed fields to the output"""
        data = super().to_representation(instance)
        
        # Add status information
        status = []
        if instance.Suspended:
            status.append('Suspended')
        if instance.Lapsed:
            status.append('Lapsed')
        if instance.is_deleted:
            status.append('Deleted')
        data['status'] = status if status else ['Active']
        
        # Add entity statistics
        entities = instance.entities.all()
        data['statistics'] = {
            'total_entities': entities.count(),
            'active_entities': entities.filter(is_deleted=False).count(),
            'suspended_entities': entities.filter(Suspended=True).count(),
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

class InstanceListSerializer(InstanceSerializer):
    """Simplified serializer for list views"""
    class Meta(InstanceSerializer.Meta):
        fields = [
            'instanceID',
            'instanceName',
            'industry_title',
            'status',
            'entities_count',
        ]

class InstanceSimpleSerializer(serializers.ModelSerializer):
    """Minimal serializer for nested relationships"""
    class Meta:
        model = Instance
        fields = [
            'instanceID',
            'instanceName',
        ]