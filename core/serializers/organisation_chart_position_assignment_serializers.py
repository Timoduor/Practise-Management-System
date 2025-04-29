from rest_framework import serializers
from core.models.organisation_chart_position_assignment import OrganisationChartPositionAssignment
from .base_serializers import BaseModelSerializer
from .organisation_chart_serializers import OrganisationChartSimpleSerializer
from .entity_serializers import EntitySerializer


class OrganisationChartPositionAssignmentSerializer(BaseModelSerializer):
    """
    Main serializer for OrganisationChartPositionAssignment model with full details
    """
    # Nested relationships
    org_chart_details = OrganisationChartSimpleSerializer(source='orgChartID', read_only=True)
    entity_details = EntitySerializer(source='entityID', read_only=True)
    
    # Computed fields
    status = serializers.SerializerMethodField()
    subordinates_count = serializers.SerializerMethodField()
    superior_position = serializers.SerializerMethodField()
    hierarchy_level = serializers.SerializerMethodField()
    has_subordinates = serializers.SerializerMethodField()

    class Meta:
        model = OrganisationChartPositionAssignment
        fields = [
            'positionAssignmentID',
            'DateAdded',
            'LastUpdate',
            'orgDataID',
            'orgChartID',
            'org_chart_details',
            'entityID',
            'entity_details',
            'positionID',
            'positionTypeID',
            'positionTitle',
            'positionDescription',
            'positionParentID',
            'positionOrder',
            'positionLevel',
            'positionCode',
            'LastUpdatedByID',
            'Lapsed',
            'Suspended',
            'status',
            'subordinates_count',
            'superior_position',
            'hierarchy_level',
            'has_subordinates',
            'created_at',
            'updated_at',
            'created_by',
            'last_updated_by',
        ]
        read_only_fields = [
            'positionAssignmentID',
            'DateAdded',
            'LastUpdate',
            'created_at',
            'updated_at',
            'created_by',
            'last_updated_by',
        ]

    def get_status(self, obj):
        """Get current status of the position"""
        return obj.status

    def get_subordinates_count(self, obj):
        """Get count of direct subordinates"""
        return obj.subordinates_count

    def get_superior_position(self, obj):
        """Get details of superior position"""
        superior = obj.get_superior()
        if superior:
            return {
                'id': superior.positionID,
                'title': superior.positionTitle,
                'level': superior.positionLevel
            }
        return None

    def get_hierarchy_level(self, obj):
        """Get the hierarchical level of the position"""
        return obj.get_hierarchy_level()

    def get_has_subordinates(self, obj):
        """Check if position has subordinates"""
        return obj.has_subordinates

    def validate_positionTitle(self, value):
        """
        Validate position title:
        - Ensure proper formatting
        - Check uniqueness within org chart
        """
        value = value.strip()
        
        # Check for existing position with same title in same org chart
        org_chart_id = self.initial_data.get('orgChartID')
        if org_chart_id:
            existing = OrganisationChartPositionAssignment.objects.filter(
                positionTitle__iexact=value,
                orgChartID=org_chart_id
            ).exists()
            
            if existing and (not self.instance or self.instance.positionTitle.lower() != value.lower()):
                raise serializers.ValidationError(
                    "A position with this title already exists in this org chart."
                )
        
        return value

    def validate(self, data):
        """
        Validate the complete position assignment data:
        - Check org chart and entity status
        - Validate relationships
        - Check position hierarchy
        """
        # Check if org chart is active
        org_chart = data.get('orgChartID')
        if org_chart and org_chart.Suspended == 'Y':
            raise serializers.ValidationError({
                'orgChartID': "Cannot create/update position in a suspended org chart."
            })

        # Check if entity is active
        entity = data.get('entityID')
        if entity and entity.is_deleted:
            raise serializers.ValidationError({
                'entityID': "Cannot create/update position for an inactive entity."
            })

        # Validate parent position exists if not top level
        parent_id = data.get('positionParentID')
        if parent_id and parent_id != 0:
            try:
                parent = OrganisationChartPositionAssignment.objects.get(
                    orgChartID=org_chart,
                    positionID=parent_id
                )
                if parent.Suspended == 'Y':
                    raise serializers.ValidationError({
                        'positionParentID': "Cannot assign to a suspended parent position."
                    })
            except OrganisationChartPositionAssignment.DoesNotExist:
                raise serializers.ValidationError({
                    'positionParentID': "Parent position does not exist."
                })

        return data

    def create(self, validated_data):
        """Create position with proper user tracking"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['LastUpdatedByID'] = request.user
            if hasattr(self.Meta.model, 'created_by'):
                validated_data['created_by'] = request.user
                
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update position with proper user tracking"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['LastUpdatedByID'] = request.user
            
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Enhance the output representation"""
        data = super().to_representation(instance)
        
        # Add subordinates information
        subordinates = instance.get_subordinates()
        data['subordinates'] = {
            'count': subordinates.count(),
            'positions': [
                {
                    'id': sub.positionID,
                    'title': sub.positionTitle,
                    'level': sub.positionLevel
                }
                for sub in subordinates
            ] if subordinates.exists() else []
        }
        
        # Format dates
        if data.get('DateAdded'):
            data['DateAdded'] = instance.DateAdded.strftime('%Y-%m-%d %H:%M:%S')
        if data.get('LastUpdate'):
            data['LastUpdate'] = instance.LastUpdate.strftime('%Y-%m-%d %H:%M:%S')
            
        return data


class OrganisationChartPositionListSerializer(OrganisationChartPositionAssignmentSerializer):
    """
    Simplified serializer for list views
    """
    class Meta(OrganisationChartPositionAssignmentSerializer.Meta):
        fields = [
            'positionAssignmentID',
            'positionTitle',
            'positionLevel',
            'positionCode',
            'org_chart_details',
            'status',
            'subordinates_count',
            'LastUpdate',
        ]


class OrganisationChartPositionSimpleSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for nested relationships
    """
    class Meta:
        model = OrganisationChartPositionAssignment
        fields = [
            'positionAssignmentID',
            'positionTitle',
            'positionLevel',
        ]