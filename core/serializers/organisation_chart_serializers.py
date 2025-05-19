from rest_framework import serializers
from core.models.organisation_chart import OrganisationChart
from core.models.organisation_data import OrganisationData
from .base_serializers import BaseModelSerializer
from .entity_serializers import EntitySerializer


class OrganisationDataSerializer(serializers.ModelSerializer):
    """
    Serializer for OrganisationData model
    """
    class Meta:
        model = OrganisationData
        fields = [
            'orgDataID',
            'orgName',
            'orgLogo',
            # Include other relevant fields from your OrganisationData model
        ]


class OrganisationChartSerializer(BaseModelSerializer):
    """
    Main serializer for OrganisationChart model with full details
    """
    # Nested relationships
    entity_details = EntitySerializer(source='entityID', read_only=True)
    org_data_details = OrganisationDataSerializer(source='orgDataID', read_only=True)
    
    # Computed fields
    status = serializers.SerializerMethodField()
    positions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = OrganisationChart
        fields = [
            'orgChartID',
            'DateAdded',
            'orgChartName',
            'orgDataID',
            'org_data_details',
            'entityID',
            'entity_details',
            'LastUpdate',
            'LastUpdatedByID',
            'Lapsed',
            'Suspended',
            'status',
            'positions_count',
            'created_at',
            'updated_at',
            'created_by',
            'last_updated_by',
        ]
        read_only_fields = [
            'orgChartID',
            'DateAdded',
            'LastUpdate',
            'created_at',
            'updated_at',
            'created_by',
            'last_updated_by',
        ]

    def get_status(self, obj):
        """Get the current status of the organization chart"""
        return obj.status

    def get_positions_count(self, obj):
        """Get count of positions in this org chart"""
        return obj.position_assignments.count()

    def validate_orgChartName(self, value):
        """
        Validate the organization chart name:
        - Ensure uniqueness within the entity
        - Proper formatting
        """
        value = value.strip()
        
        # Check for existing org chart with same name in same entity
        entity_id = self.initial_data.get('entityID')
        if entity_id:
            existing = OrganisationChart.objects.filter(
                orgChartName__iexact=value,
                entityID=entity_id
            ).exists()
            
            if existing and (not self.instance or self.instance.orgChartName.lower() != value.lower()):
                raise serializers.ValidationError(
                    "An organization chart with this name already exists in this entity."
                )
        
        return value

    def validate(self, data):
        """
        Validate the complete organization chart data:
        - Check entity status
        - Validate relationships
        """
        # Check if entity is active
        entity = data.get('entityID')
        if entity and entity.is_deleted:
            raise serializers.ValidationError({
                'entityID': "Cannot create/update org chart for an inactive entity."
            })
            
        return data

    def create(self, validated_data):
        """Create organization chart with proper user tracking"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['LastUpdatedByID'] = request.user
            if hasattr(self.Meta.model, 'created_by'):
                validated_data['created_by'] = request.user
                
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update organization chart with proper user tracking"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['LastUpdatedByID'] = request.user
            
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Enhance the output representation"""
        data = super().to_representation(instance)
        
        # Add position statistics
        positions = instance.position_assignments.all()
        data['statistics'] = {
            'total_positions': positions.count(),
            'active_positions': positions.filter(Suspended='N', Lapsed='N').count(),
            'suspended_positions': positions.filter(Suspended='Y').count(),
            'lapsed_positions': positions.filter(Lapsed='Y').count(),
        }
        
        # Format dates
        if data.get('DateAdded'):
            data['DateAdded'] = instance.DateAdded.strftime('%Y-%m-%d %H:%M:%S')
        if data.get('LastUpdate'):
            data['LastUpdate'] = instance.LastUpdate.strftime('%Y-%m-%d %H:%M:%S')
            
        return data


class OrganisationChartListSerializer(OrganisationChartSerializer):
    """
    Simplified serializer for list views
    """
    class Meta(OrganisationChartSerializer.Meta):
        fields = [
            'orgChartID',
            'orgChartName',
            'entityID',
            'entity_details',
            'orgDataID',
            'org_data_details',
            'status',
            'positions_count',
            'LastUpdate',
        ]


class OrganisationChartSimpleSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for nested relationships
    """
    class Meta:
        model = OrganisationChart
        fields = [
            'orgChartID',
            'orgChartName',
        ]