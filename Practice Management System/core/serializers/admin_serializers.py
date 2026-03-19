from rest_framework import serializers
from core.models.user import User
from core.models.admin import Admin
from core.models.admin_type import AdminType
from core.models.instance import Instance
from core.models.entity import Entity
from core.models.unit import Unit
from .base_serializers import SoftDeleteMixin
from django.contrib.contenttypes.models import ContentType
from .user_serializers import UserSerializer

class AdminSerializer(serializers.ModelSerializer, SoftDeleteMixin):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=True
    )
    user_detail = UserSerializer(
        source="user",
        read_only=True
    )
    admin_type = serializers.PrimaryKeyRelatedField(
        queryset=AdminType.objects.all(),
        required=True
    )
    jurisdiction_name = serializers.SerializerMethodField()
    is_active = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Admin
        fields = [
            'id',
            'user',
            'user_detail',
            'admin_type',
            'jurisdiction_content_type',
            'jurisdiction_object_id',
            'jurisdiction_name',
            'is_active',
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

    def get_jurisdiction_name(self, obj):
        """Returns the name of the jurisdiction object"""
        if obj.jurisdiction:
            return str(obj.jurisdiction)
        return None

    def validate(self, data):
        """Validate the admin data"""
        user = data.get('user')
        admin_type = data.get('admin_type')

        if not user or not admin_type:
            raise serializers.ValidationError(
                "Both user and admin_type are required."
            )

        # Set jurisdiction based on admin_type
        if admin_type.name == "ENT":
            data['jurisdiction_content_type'] = ContentType.objects.get_for_model(Entity)
        elif admin_type.name == "UNI":
            data['jurisdiction_content_type'] = ContentType.objects.get_for_model(Unit)
        elif admin_type.name == "INS":
            data['jurisdiction_content_type'] = ContentType.objects.get_for_model(Instance)
        else:
            data['jurisdiction_content_type'] = None
            data['jurisdiction_object_id'] = None

        # Validate jurisdiction object if content type is set
        if data.get('jurisdiction_content_type') and data.get('jurisdiction_object_id'):
            try:
                model_class = data['jurisdiction_content_type'].model_class()
                jurisdiction_obj = model_class.objects.get(pk=data['jurisdiction_object_id'])
                
                # Validate that user has access to this jurisdiction
                if hasattr(user, 'employee_user'):
                    employee = user.employee_user
                    if admin_type.name == "ENT" and employee.entity_id != jurisdiction_obj.id:
                        raise serializers.ValidationError(
                            "User does not have access to this entity."
                        )
                    elif admin_type.name == "UNI" and employee.unit_id != jurisdiction_obj.id:
                        raise serializers.ValidationError(
                            "User does not have access to this unit."
                        )
                    elif admin_type.name == "INS" and employee.instance_id != jurisdiction_obj.id:
                        raise serializers.ValidationError(
                            "User does not have access to this instance."
                        )
            except model_class.DoesNotExist:
                raise serializers.ValidationError(
                    f"Invalid jurisdiction object ID for {model_class.__name__}"
                )

        return data

    def create(self, validated_data):
        """Create new admin with proper user tracking"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
            validated_data['last_updated_by'] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update admin with proper user tracking"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['last_updated_by'] = request.user
        return super().update(instance, validated_data)