from rest_framework import serializers
from core.models.organisation_data import OrganisationData
from .base_serializers import BaseModelSerializer
from core.serializers.user_serializers import UserSimpleSerializer


class OrganisationDataSerializer(BaseModelSerializer):
    """
    Main serializer for OrganisationData model with full details
    """
    # Nested relationships
    instance_details = serializers.SerializerMethodField()
    industry_sector_details = serializers.SerializerMethodField()
    last_updated_by = UserSimpleSerializer(source='LastUpdatedByID', read_only=True)
    
    # Computed fields
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = OrganisationData
        fields = [
            'orgDataID',
            'DateAdded',
            'instanceID',
            'instance_details',
            'orgLogo',
            'orgName',
            'industrySectorID',
            'industry_sector_details',
            'numberOfEmployees',
            'registrationNumber',
            'orgPIN',
            'costCenterEnabled',
            'orgAddress',
            'orgPostalCode',
            'orgCity',
            'orgCountry',
            'orgPhoneNumber1',
            'orgPhoneNumber2',
            'orgEmail',
            'LastUpdate',
            'LastUpdatedByID',
            'last_updated_by',
            'Lapsed',
            'Suspended',
            'status',
        ]
        read_only_fields = [
            'orgDataID',
            'DateAdded',
            'LastUpdate',
        ]

    def get_status(self, obj):
        """Get the current status of the organisation data"""
        if obj.Suspended == 'YES':
            return 'Suspended'
        elif obj.Lapsed == 'YES':
            return 'Lapsed'
        else:
            return 'Active'

    def get_instance_details(self, obj):
        """Get instance details"""
        if obj.instanceID:
            return {
                'id': obj.instanceID.id,
                'name': str(obj.instanceID)
            }
        return None

    def get_industry_sector_details(self, obj):
        """Get industry sector details"""
        if obj.industrySectorID:
            return {
                'id': obj.industrySectorID.id,
                'name': str(obj.industrySectorID)
            }
        return None

    def validate_orgEmail(self, value):
        """Validate email address"""
        # Email validation is handled by the EmailField, but you can add custom validation here
        return value

    def validate_orgName(self, value):
        """Validate organisation name is unique"""
        # Check if org name already exists (case insensitive)
        instance_id = self.initial_data.get('instanceID')
        if instance_id:
            exists = OrganisationData.objects.filter(
                orgName__iexact=value, 
                instanceID=instance_id
            ).exclude(pk=getattr(self.instance, 'orgDataID', None)).exists()
            
            if exists:
                raise serializers.ValidationError(
                    "An organisation with this name already exists in this instance."
                )
        return value

    def validate(self, data):
        """Validate the entire payload"""
        # Ensure we don't have conflicting status
        if data.get('Suspended') == 'YES' and data.get('Lapsed') == 'YES':
            raise serializers.ValidationError(
                "An organisation cannot be both Suspended and Lapsed simultaneously."
            )
        return data

    def update(self, instance, validated_data):
        """Update with user tracking"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['LastUpdatedByID'] = request.user
        return super().update(instance, validated_data)

    def create(self, validated_data):
        """
        Override create method to handle field conversions and user tracking
        """
        # Remove fields that don't exist in the model
        created_by = validated_data.pop('created_by', None)
        last_updated_by = validated_data.pop('last_updated_by', None)
        
        # Set the correct field name for user tracking
        if last_updated_by:
            validated_data['LastUpdatedByID'] = last_updated_by
        
        # Create the organisation data instance
        instance = OrganisationData.objects.create(**validated_data)
        
        return instance

    def suspend(self, obj):
        """Suspend organisation"""
        obj.Suspended = 'YES'
        obj.save()
    
    def unsuspend(self, obj):
        """Unsuspend organisation"""
        obj.Suspended = 'NO'
        obj.save()
    
    def lapse(self, obj):
        """Mark organisation as lapsed"""
        obj.Lapsed = 'YES'
        obj.save()
    
    def unlapse(self, obj):
        """Remove lapsed status"""
        obj.Lapsed = 'NO'
        obj.save()


class OrganisationDataListSerializer(OrganisationDataSerializer):
    """
    Simplified serializer for list views
    """
    class Meta(OrganisationDataSerializer.Meta):
        fields = [
            'orgDataID',
            'orgName',
            'orgEmail',
            'orgCity',
            'orgCountry',
            'status',
            'LastUpdate',
        ]


class OrganisationDataSimpleSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for nested relationships
    """
    class Meta:
        model = OrganisationData
        fields = [
            'orgDataID',
            'orgName',
            'orgEmail',
        ]