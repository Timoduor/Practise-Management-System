from rest_framework import serializers
from django.utils import timezone
from core.models.user import User

class SoftDeleteMixin:
    """
    Mixin class to provide soft delete functionality for serializers.
    Works with models inheriting from SoftDeleteModel.
    """
    def perform_soft_delete(self, instance):
        """Perform soft delete on the instance"""
        instance.delete()
        return instance

    def perform_restore(self, instance):
        """Restore a soft-deleted instance"""
        instance.undelete()
        return instance

    def perform_hard_delete(self, instance):
        """Permanently delete the instance"""
        instance.hard_delete()
        return True

    def validate(self, attrs):
        """Add user tracking to validated data"""
        request = self.context.get('request')
        if request and request.user:
            if not self.instance:  # Creating new instance
                attrs['created_by'] = request.user
            attrs['last_updated_by'] = request.user
        return super().validate(attrs)

    def to_representation(self, instance):
        """Add common soft delete fields to representation"""
        data = super().to_representation(instance)
        data.update({
            'is_deleted': instance.is_deleted,
            'created_at': instance.created_at.isoformat() if instance.created_at else None,
            'updated_at': instance.updated_at.isoformat() if instance.updated_at else None,
            'created_by': instance.created_by.id if instance.created_by else None,
            'last_updated_by': instance.last_updated_by.id if instance.last_updated_by else None,
        })
        return data

class SoftDeleteModelSerializer(serializers.ModelSerializer):
    """
    Base ModelSerializer for models inheriting from SoftDeleteModel.
    Includes common fields and functionality.
    """
    is_deleted = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False
    )
    last_updated_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False
    )

    class Meta:
        abstract = True
        read_only_fields = (
            'is_deleted',
            'created_at',
            'updated_at',
            'created_by',
            'last_updated_by',
        )

    def create(self, validated_data):
        """Handle creation with user tracking"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
            validated_data['last_updated_by'] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Handle updates with user tracking"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['last_updated_by'] = request.user
            validated_data['updated_at'] = timezone.now()
        return super().update(instance, validated_data)

    def perform_destroy(self, instance):
        """Handle soft delete"""
        instance.delete()
        return instance

class BaseModelSerializer(SoftDeleteModelSerializer, SoftDeleteMixin):
    """
    Combined base serializer with both soft delete functionality
    and common model serializer features.
    """
    class Meta(SoftDeleteModelSerializer.Meta):
        abstract = True

    def get_fields(self):
        """Add common fields to all serializers"""
        fields = super().get_fields()
        return fields