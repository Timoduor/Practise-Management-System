from rest_framework import serializers
from core.models.user import User
from core.models.employee import Employee
from core.models.instance import Instance
from core.models.entity import Entity
from core.models.unit import Unit
from .base_serializers import BaseModelSerializer
from .user_serializers import UserSerializer
import logging
from core.models.organisation_role import OrganisationRole
from core.permissions.base_permissions import ROLE_HIERARCHY


logger = logging.getLogger(__name__)

class EmployeeSerializer(BaseModelSerializer):
    """
    Serializer for Employee model with nested relationships and proper tracking
    """
    # Nested relationships
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    user_detail = UserSerializer(source='user', read_only=True)
    
    # Related fields with proper serialization
    instance = serializers.PrimaryKeyRelatedField(
        queryset=Instance.objects.all(),
        required=True
    )
    entity = serializers.PrimaryKeyRelatedField(
        queryset=Entity.objects.all(),
        required=False,
        allow_null=True
    )
    unit = serializers.PrimaryKeyRelatedField(
        queryset=Unit.objects.all(),
        required=False,
        allow_null=True
    )

    # Readable names for related objects
    instance_name = serializers.CharField(source='instance.instanceName', read_only=True)
    entity_name = serializers.CharField(source='entity.entityName', read_only=True)
    unit_name = serializers.CharField(source='unit.name', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id',
            'user',
            'user_detail',
            'instance',
            'instance_name',
            'entity',
            'entity_name',
            'unit',
            'unit_name',
            'is_deleted',
            'created_at',
            'updated_at',
            'created_by',
            'last_updated_by',
        ]
        read_only_fields = [
            'created_at',
            'updated_at',
            'created_by',
            'last_updated_by',
        ]

    def validate(self, data):
        """
        Validate the employee data:
        - Ensure entity belongs to instance if provided
        - Ensure unit belongs to entity if provided
        """
        instance = data.get('instance')
        entity = data.get('entity')
        unit = data.get('unit')

        if entity and entity.instanceID != instance:
            raise serializers.ValidationError({
                'entity': 'Entity must belong to the specified instance.'
            })

        if unit:
            if not entity:
                raise serializers.ValidationError({
                    'unit': 'Cannot assign unit without an entity.'
                })
            if unit.entity != entity:
                raise serializers.ValidationError({
                    'unit': 'Unit must belong to the specified entity.'
                })

        return super().validate(data)

    def create(self, validated_data):
        """Create employee with proper user tracking"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
            validated_data['last_updated_by'] = request.user
        
        logger.info(
            "Creating new employee for user %s in instance %s",
            validated_data.get('user'),
            validated_data.get('instance')
        )
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Update employee with proper authorization and tracking
        """
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError({
                'authorization': 'No authenticated user found.'
            })

        # Check authorization
        if not (request.user.is_staff or request.user == instance.user):
            raise serializers.ValidationError({
                'authorization': 'You are not authorized to update this employee data.'
            })

        validated_data['last_updated_by'] = request.user
        
        logger.info(
            "Updating employee %s by user %s",
            instance,
            request.user
        )

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """
        Add additional computed fields to the output
        """
        data = super().to_representation(instance)
        
        # Add user's full name for convenience
        if instance.user:
            data['user_full_name'] = f"{instance.user.first_name} {instance.user.last_name}"
        
        # Add hierarchical path
        hierarchy = []
        if instance.instance:
            hierarchy.append(instance.instance.instanceName)
        if instance.entity:
            hierarchy.append(instance.entity.entityName)
        if instance.unit:
            hierarchy.append(instance.unit.name)
        data['organizational_path'] = ' > '.join(hierarchy)

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