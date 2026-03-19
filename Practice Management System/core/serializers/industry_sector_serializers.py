from rest_framework import serializers
from core.models.industry_sector import IndustrySector
from .user_serializers import UserSerializer

class IndustrySectorSerializer(serializers.ModelSerializer):
    """
    Serializer for IndustrySector model with proper field mapping and relationships
    """
    # Nested serializer for user details
    last_updated_by_detail = UserSerializer(source='LastUpdatedByID', read_only=True)
    
    # Count of related entities and instances
    entities_count = serializers.SerializerMethodField()
    instances_count = serializers.SerializerMethodField()

    class Meta:
        model = IndustrySector
        fields = [
            'industrySectorID',
            'DateAdded',
            'industryTitle',
            'industryCategory',
            'LastUpdatedByID',
            'last_updated_by_detail',
            'Suspended',
            'entities_count',
            'instances_count'
        ]
        read_only_fields = [
            'industrySectorID',
            'DateAdded',
            'LastUpdatedByID',
            'entities_count',
            'instances_count'
        ]

    def get_entities_count(self, obj):
        """Get count of entities in this sector"""
        return obj.entities.count()

    def get_instances_count(self, obj):
        """Get count of instances in this sector"""
        return obj.instances.count()

    def validate_industryTitle(self, value):
        """
        Validate the industry title:
        - Ensure it's unique
        - Proper formatting
        """
        value = value.strip().title()
        
        # Check uniqueness
        if IndustrySector.objects.filter(industryTitle=value).exists():
            if not self.instance or self.instance.industryTitle != value:
                raise serializers.ValidationError(
                    "An industry sector with this title already exists."
                )
        return value

    def validate_industryCategory(self, value):
        """
        Validate the industry category:
        - Proper formatting
        """
        return value.strip().title()

    def create(self, validated_data):
        """Create industry sector with proper user tracking"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['LastUpdatedByID'] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update industry sector with proper user tracking"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['LastUpdatedByID'] = request.user
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Add additional computed fields to the output"""
        data = super().to_representation(instance)
        
        # Add status information
        data['status'] = 'Suspended' if instance.Suspended == 'Y' else 'Active'
        
        # Add formatted dates
        if instance.DateAdded:
            data['DateAdded_formatted'] = instance.DateAdded.strftime('%Y-%m-%d %H:%M:%S')
        
        return data

class IndustrySectorListSerializer(IndustrySectorSerializer):
    """Simplified serializer for list views"""
    class Meta(IndustrySectorSerializer.Meta):
        fields = [
            'industrySectorID',
            'industryTitle',
            'industryCategory',
            'status',
            'entities_count',
            'instances_count'
        ]

class IndustrySectorSimpleSerializer(serializers.ModelSerializer):
    """Minimal serializer for nested relationships"""
    class Meta:
        model = IndustrySector
        fields = [
            'industrySectorID',
            'industryTitle',
            'industryCategory'
        ]