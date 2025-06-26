from rest_framework import serializers
from core.models.organisation_chart_position_assignment import OrganisationChartPositionAssignment
from .base_serializers import BaseModelSerializer
from .organisation_chart_serializers import OrganisationChartSimpleSerializer
from core.models.organisation_role import OrganisationRole
from core.permissions.base_permissions import ROLE_HIERARCHY


class OrganisationChartPositionAssignmentSerializer(BaseModelSerializer):
    """
    Main serializer for OrganisationChartPositionAssignment model with full details
    """
    # Nested relationships
    org_chart_details = OrganisationChartSimpleSerializer(source='orgChartID', read_only=True)
    parent_position = serializers.SerializerMethodField()
    
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
            'orgChartID',
            'org_chart_details',
            'positionID',
            'positionTitle',
            'positionDescription',
            'positionParentID',
            'parent_position',
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
            'updated_at',
            'last_updated_by',
        ]
        read_only_fields = [
            'positionAssignmentID',
            'DateAdded',
            'LastUpdate',
            'positionOrder',  # Auto-generated
            'positionLevel',  # Auto-generated
            'positionCode',   # Auto-generated
            'updated_at',
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
                'id': superior.positionAssignmentID,
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

    def get_parent_position(self, obj):
        """Get the parent position details"""
        if obj.positionParentID:
            return {
                'id': obj.positionParentID.positionAssignmentID,
                'title': obj.positionParentID.positionTitle
            }
        return None

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
        - Check org chart status
        - Validate relationships
        - Check position hierarchy
        """
        # Check if org chart is active
        org_chart = data.get('orgChartID')
        if org_chart and org_chart.Suspended == 'Y':
            raise serializers.ValidationError({
                'orgChartID': "Cannot create/update position in a suspended org chart."
            })

        # Validate parent position is in the same org chart
        parent = data.get('positionParentID')
        org_chart_id = data.get('orgChartID')
        
        if parent and org_chart_id and parent.orgChartID != org_chart_id:
            raise serializers.ValidationError({
                'positionParentID': "Parent position must be in the same org chart."
            })

        return data

    def update(self, instance, validated_data):
        """Update position with proper user tracking"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['LastUpdatedByID'] = request.user
            
        return super().update(instance, validated_data)
    
    
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

    def to_representation(self, instance):
        """Enhance the output representation"""
        data = super().to_representation(instance)
        
        # Add subordinates information
        subordinates = instance.get_subordinates()
        data['subordinates'] = {
            'count': subordinates.count(),
            'positions': [
                {
                    'id': sub.positionAssignmentID,
                    'title': sub.positionTitle,
                    'level': sub.positionLevel
                }
                for sub in subordinates[:5]  # Limit to first 5 for performance
            ] if subordinates.exists() else []
        }
        
        # Add entity information via org chart
        if instance.orgChartID and instance.orgChartID.entityID:
            entity = instance.orgChartID.entityID
            data['entity_info'] = {
                'id': entity.entityID,
                'name': entity.entityName if hasattr(entity, 'entityName') else str(entity)
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