from rest_framework import serializers
from .base_serializers import BaseModelSerializer
from core.models.entity_type import EntityType
from .user_serializers import UserSerializer

class EntityTypeSerializer(BaseModelSerializer):
    """
    Serializer for EntityType model with proper field mapping and tracking
    """
    # Nested serializers for user tracking
    created_by_detail = UserSerializer(source='created_by', read_only=True)
    last_updated_by_detail = UserSerializer(source='last_updated_by', read_only=True)
    
    # Count of entities using this type
    entities_count = serializers.SerializerMethodField()

    class Meta:
        model = EntityType
        fields = [
            'entityTypeID',
            'DateAdded',
            'entityTypeTitle',
            'entityTypeDescription',
            'LastUpdate',
            'Lapsed',
            'Suspended',
            'is_deleted',
            'created_at',
            'updated_at',
            'created_by',
            'created_by_detail',
            'last_updated_by',
            'last_updated_by_detail',
            'entities_count'
        ]
        read_only_fields = [
            'entityTypeID',
            'DateAdded',
            'LastUpdate',
            'created_at',
            'updated_at',
            'created_by',
            'last_updated_by',
            'entities_count'
        ]

    def get_entities_count(self, obj):
        """Get count of entities using this type"""
        return obj.entities.count()

    def validate_entityTypeTitle(self, value):
        """
        Validate the entity type title:
        - Ensure it's unique
        - Convert to proper format
        """
        # Convert to title case
        value = value.strip().title()

        # Check uniqueness
        if EntityType.objects.filter(entityTypeTitle=value).exists():
            if not self.instance or self.instance.entityTypeTitle != value:
                raise serializers.ValidationError(
                    "An entity type with this title already exists."
                )
        return value

    def create(self, validated_data):
        """Create entity type with proper user tracking"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
            validated_data['last_updated_by'] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update entity type with proper user tracking"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['last_updated_by'] = request.user
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

        return data

class EntityTypeListSerializer(EntityTypeSerializer):
    """Simplified serializer for list views"""
    class Meta(EntityTypeSerializer.Meta):
        fields = [
            'entityTypeID',
            'entityTypeTitle',
            'entities_count',
            'status',
        ]