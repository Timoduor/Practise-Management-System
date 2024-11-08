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

import string, secrets
from django.core.mail import send_mail

# Serializer for Admin model with SoftDeleteMixin
class AdminSerializer(serializers.ModelSerializer, SoftDeleteMixin):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  # Primary key field for user
    user_detail = UserSerializer(source="user", read_only=True)
    admin_type = serializers.SlugRelatedField(slug_field='name', queryset=AdminType.objects.all())  # Admin type field
    jurisdiction_name = serializers.SerializerMethodField() 

    class Meta:
        model = Admin
        fields = ['id', 'user','user_detail' ,'admin_type', 'jurisdiction_content_type', 'jurisdiction_object_id', "jurisdiction_name"]


    def get_jurisdiction_name(self, obj):
        """
        Returns the name of the instance, entity, or unit based on the admin type.
        """
        if obj.admin_type.name == "INS" and obj.jurisdiction_object_id:
            try:
                instance = Instance.objects.get(pk=obj.jurisdiction_object_id)
                return instance.name
            except Instance.DoesNotExist:
                return None
        elif obj.admin_type.name == "ENT" and obj.jurisdiction_object_id:
            try:
                entity = Entity.objects.get(pk=obj.jurisdiction_object_id)
                return entity.name
            except Entity.DoesNotExist:
                return None
        elif obj.admin_type.name == "UNI" and obj.jurisdiction_object_id:
            try:
                unit = Unit.objects.get(pk=obj.jurisdiction_object_id)
                return unit.name
            except Unit.DoesNotExist:
                return None
        return None
   
    def validate(self, data):
        # Ensure 'user' is an ID
        user_id = data['user']
        
        # If `user` is a User instance instead of an ID, replace it with its ID
        if isinstance(user_id, User):
            user_id = user_id.id
        data['user'] = user_id  # Assign back the ID to data['user']

        # Fetch the full User instance with related employee fields
        try:
            user = User.objects.select_related(
                'employee_user__instance', 'employee_user__entity', 'employee_user__unit'
            ).get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({"user": "User with the given ID does not exist."})

        # Temporarily store user instance for validation purposes
        admin_type_name = data['admin_type']

        # Use get_or_create to ensure the admin type exists or create it if it doesn't
        admin_type, created = AdminType.objects.get_or_create(
            name=admin_type_name,
            defaults={'description': f'{admin_type_name} Admin Type'}
        )
        data['admin_type'] = admin_type  # Replace the name with the actual AdminType instance

        # Determine jurisdiction based on admin_type
        if admin_type.name == "INS":
            if user.employee_user and user.employee_user.instance:
                data['jurisdiction_content_type'] = ContentType.objects.get_for_model(Instance)
                data['jurisdiction_object_id'] = user.employee_user.instance.id
            else:
                raise serializers.ValidationError({
                    'jurisdiction': 'User does not have an associated instance.'
                })
        elif admin_type.name == "ENT":
            if user.employee_user and user.employee_user.entity:
                data['jurisdiction_content_type'] = ContentType.objects.get_for_model(Entity)
                data['jurisdiction_object_id'] = user.employee_user.entity.id
            else:
                raise serializers.ValidationError({
                    'jurisdiction': 'User does not have an associated entity.'
                })
        elif admin_type.name == "UNI":
            if user.employee_user and user.employee_user.unit:
                data['jurisdiction_content_type'] = ContentType.objects.get_for_model(Unit)
                data['jurisdiction_object_id'] = user.employee_user.unit.id
            else:
                raise serializers.ValidationError({
                    'jurisdiction': 'User does not have an associated unit.'
                })
        else:
            raise serializers.ValidationError({
                'admin_type': 'Invalid admin type specified.'
            })

        return data

    def create(self, validated_data):
        # Convert 'user' ID to User instance if it's not already
        if isinstance(validated_data['user'], int):
            validated_data['user'] = User.objects.get(id=validated_data['user'])
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Convert 'user' ID to User instance if it's not already
        if isinstance(validated_data['user'], int):
            validated_data['user'] = User.objects.get(id=validated_data['user'])
        
        return super().update(instance, validated_data)

