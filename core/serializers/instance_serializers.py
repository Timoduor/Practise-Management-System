from rest_framework import serializers
from .entity_serializers import EntitySerializer
from .base_serializers import BaseModelSerializer
from core.models.instance import Instance
from core.models.industry_sector import IndustrySector

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
    industry_title = serializers.CharField(source='industrySector.industryTitle', read_only=True)
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