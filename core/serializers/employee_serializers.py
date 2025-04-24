from rest_framework import serializers
from core.models.user import User
from core.models.employee import Employee
from core.models.instance import Instance
from core.models.entity import Entity
from core.models.unit import Unit
from .base_serializers import BaseModelSerializer
from .user_serializers import UserSerializer
import logging

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
            data['user_full_name'] = f"{instance.user.firstName} {instance.user.surname}"
        
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