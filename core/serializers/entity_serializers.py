from rest_framework import serializers
from .base_serializers import BaseModelSerializer
from .unit_serializers import UnitSerializer
from core.models.entity import Entity
from core.models.industry_sector import IndustrySector
from core.models.organisation_data import OrganisationData

class EntitySerializer(BaseModelSerializer):
    """
    Serializer for Entity model with nested relationships and proper tracking
    """
    # Nested relationships
    units = UnitSerializer(many=True, read_only=True)
    
    # Related fields
    entityTypeID = serializers.PrimaryKeyRelatedField(
        source='entityTypeID',
        queryset=Entity.objects.all(),
        required=True
    )
    
    instanceID = serializers.PrimaryKeyRelatedField(
        source='instanceID',
        queryset=Entity.objects.all(),
        required=False,
        allow_null=True
    )
    
    orgDataID = serializers.PrimaryKeyRelatedField(
        source='orgDataID',
        queryset=OrganisationData.objects.all(),
        required=False,
        allow_null=True
    )
    
    entityParentID = serializers.PrimaryKeyRelatedField(
        source='entityParentID',
        queryset=Entity.objects.all(),
        required=False,
        allow_null=True
    )
    
    industrySectorID = serializers.PrimaryKeyRelatedField(
        source='industrySectorID',
        queryset=IndustrySector.objects.all(),
        required=False,
        allow_null=True
    )

    # Readable names for related objects
    entityType_name = serializers.CharField(source='entityTypeID.entityTypeTitle', read_only=True)
    parent_name = serializers.CharField(source='entityParentID.entityName', read_only=True)
    industry_name = serializers.CharField(source='industrySectorID.industryTitle', read_only=True)
    
    # Child entities
    child_entities = serializers.SerializerMethodField()

    class Meta:
        model = Entity
        fields = [
            'entityID',
            'DateAdded',
            'entityName',
            'entityDescription',
            'entityTypeID',
            'entityType_name',
            'instanceID',
            'orgDataID',
            'entityParentID',
            'parent_name',
            'industrySectorID',
            'industry_name',
            'registrationNumber',
            'entityPIN',
            'entityCity',
            'entityCountry',
            'entityPhoneNumber',
            'entityEmail',
            'LastUpdate',
            'LastUpdateByID',
            'Lapsed',
            'Suspended',
            'child_entities',
            'units',
            'is_deleted',
            'created_at',
            'updated_at',
            'created_by',
            'last_updated_by',
        ]
        read_only_fields = [
            'entityID',
            'DateAdded',
            'LastUpdate',
            'LastUpdateByID',
            'created_at',
            'updated_at',
            'created_by',
            'last_updated_by',
        ]

    def get_child_entities(self, obj):
        """Get all child entities"""
        children = Entity.objects.filter(entityParentID=obj)
        return EntityListSerializer(children, many=True).data

    def validate(self, data):
        """
        Validate the entity data:
        - Ensure parent entity belongs to same instance if provided
        - Validate entity type
        - Check for circular parent references
        """
        instance = data.get('instanceID')
        parent = data.get('entityParentID')
        
        if parent:
            # Check for circular reference
            current = parent
            while current:
                if current == self.instance:
                    raise serializers.ValidationError({
                        'entityParentID': 'Circular parent reference detected.'
                    })
                current = current.entityParentID

            # Check instance match
            if instance and parent.instanceID != instance:
                raise serializers.ValidationError({
                    'entityParentID': 'Parent entity must belong to the same instance.'
                })

        return super().validate(data)

    def create(self, validated_data):
        """Create entity with proper user tracking"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
            validated_data['last_updated_by'] = request.user
            validated_data['LastUpdateByID'] = request.user

            # If no instance provided, use user's instance
            if not validated_data.get('instanceID') and hasattr(request.user, 'employee_user'):
                validated_data['instanceID'] = request.user.employee_user.instance

        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update entity with proper user tracking"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['last_updated_by'] = request.user
            validated_data['LastUpdateByID'] = request.user

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Add additional computed fields to the output"""
        data = super().to_representation(instance)
        
        # Add status information
        data['status'] = []
        if instance.Suspended:
            data['status'].append('Suspended')
        if instance.Lapsed:
            data['status'].append('Lapsed')
        if instance.is_deleted:
            data['status'].append('Deleted')
        if not data['status']:
            data['status'].append('Active')
        
        # Add hierarchical path
        hierarchy = []
        current = instance
        while current:
            hierarchy.insert(0, current.entityName)
            current = current.entityParentID
        data['entity_path'] = ' > '.join(hierarchy)

        return data

class EntityListSerializer(EntitySerializer):
    """Simplified serializer for list views"""
    class Meta(EntitySerializer.Meta):
        fields = [
            'entityID',
            'entityName',
            'entityType_name',
            'entityCity',
            'entityCountry',
            'status',
        ]