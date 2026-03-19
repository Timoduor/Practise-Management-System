from rest_framework import serializers
from .base_serializers import SoftDeleteMixin
from core.models.admin_type import AdminType
from .user_serializers import UserSerializer

class AdminTypeSerializer(serializers.ModelSerializer, SoftDeleteMixin):
    created_by_detail = UserSerializer(source='created_by', read_only=True)
    last_updated_by_detail = UserSerializer(source='last_updated_by', read_only=True)
    admins_count = serializers.SerializerMethodField()

    class Meta:
        model = AdminType
        fields = [
            'id',
            'name',
            'description',
            'is_deleted',
            'created_at',
            'updated_at',
            'created_by',
            'created_by_detail',
            'last_updated_by',
            'last_updated_by_detail',
            'admins_count'
        ]
        read_only_fields = [
            'created_at',
            'updated_at',
            'created_by',
            'last_updated_by',
            'admins_count'
        ]

    def get_admins_count(self, obj):
        """Get count of admins using this type"""
        return obj.admin_set.count()

    def validate_name(self, value):
        """Ensure name is unique and uppercase"""
        value = value.upper()
        if AdminType.objects.filter(name=value).exists():
            raise serializers.ValidationError("An admin type with this name already exists.")
        return value

    def create(self, validated_data):
        """Create new admin type with proper user tracking"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
            validated_data['last_updated_by'] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update admin type with proper user tracking"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['last_updated_by'] = request.user
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Add additional computed fields to the output"""
        data = super().to_representation(instance)
        data['is_active'] = not instance.is_deleted
        return data