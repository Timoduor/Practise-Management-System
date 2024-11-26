from rest_framework import serializers
from core.models.user import User
from core.models.admin import Admin
from core.models.employee import Employee
from core.models.admin_type import AdminType
from core.models.instance import Instance
from core.models.entity import Entity
from core.models.unit import Unit
from .base_serializers import SoftDeleteMixin
from django.contrib.contenttypes.models import ContentType
from .user_serializers import UserSerializer

import string, secrets
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)


# Serializer for Employee model, including nested UserSerializer for user details
class EmployeeSerializer(serializers.ModelSerializer, SoftDeleteMixin):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  # Use `user` field
    user_detail = UserSerializer(source='user', read_only=True)  # Nested serialization for user details

    entity = serializers.SerializerMethodField()
    instance = serializers.SerializerMethodField()
    unit = serializers.SerializerMethodField()

    # Uncommented code for alternative user field representations
    # user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    # user = UserSerializer(read_only=True)

    class Meta:
        model = Employee
        fields = ['id', 'user', 'user_detail', 'instance', 'entity', 'unit']

    def validate(self, data):
        print("Data before validation:", self.initial_data)
        validated_data = super().validate(data)
        print("Data after validation:", validated_data)
        return validated_data

    # def update(self, instance, validated_data):
    #     # Get the request user from the context
    #     request_user = self.context['request'].user
    #     print(request_user)

    #     # Check if the request user is either an admin or the user linked to this Employee instance
    #     if request_user.is_staff or request_user == instance.user:
    #         # Pop fields specific to Employee relationships
    #         employee_instance = validated_data.pop('employee_instance', None)
    #         print(employee_instance)
    #         employee_entity = validated_data.pop('employee_entity', None)
    #         print(employee_entity)
    #         employee_unit = validated_data.pop('employee_unit', None)
    #         print(employee_unit)

    #         print(instance)
    #         print("employee_entity", employee_entity)
    #         print("unit", employee_unit)
    #         print(validated_data)

    #         # Update Employee-related fields if provided
    #         if employee_instance:
    #             instance.instance = employee_instance
    #             print("Instance", instance)
    #         if employee_entity:
    #             instance.entity = employee_entity
    #             print("Entity", instance.entity)
    #         if employee_unit:
    #             instance.unit = employee_unit
    #             print("Unit", instance.unit)
    #         # Save changes to Employee instance
    #         instance.save()
    #         print(instance.save)

    #         # Update User-related fields for the linked user object
    #         user_data = {key: validated_data[key] for key in validated_data if hasattr(instance.user, key)}
    #         for attr, value in user_data.items():
    #             setattr(instance.user, attr, value)
    #         instance.user.save()

    #         # Return updated Employee instance
    #         return instance
    #     else:
    #         # Raise error if not authorized to perform the update
    #         raise serializers.ValidationError({
    #             'authorization': 'You are not authorized to update this employee data.'
    #         })

    def update(self, instance, validated_data):
        request_user = self.context['request'].user
        logger.info("Updating Employee instance. Request user: %s", request_user)

        if request_user.is_staff or request_user == instance.user:
            # Extract Employee-related fields from validated data
            employee_instance = validated_data.pop('employee_instance', None)
            employee_entity = validated_data.pop('employee_entity', None)
            employee_unit = validated_data.pop('employee_unit', None)

            logger.debug("Instance before update: %s", instance)
            logger.debug("Extracted instance: %s", employee_instance)
            logger.debug("Extracted entity: %s", employee_entity)
            logger.debug("Extracted unit: %s", employee_unit)
            logger.debug("Remaining validated data: %s", validated_data)

            # Update instance fields if provided
            if employee_instance:
                instance.instance = employee_instance
                logger.info("Updated instance field to: %s", employee_instance)
            if employee_entity:
                instance.entity = employee_entity
                logger.info("Updated entity field to: %s", employee_entity)
            if employee_unit:
                instance.unit = employee_unit
                logger.info("Updated unit field to: %s", employee_unit)

            # Save the updated Employee instance
            instance.save()
            logger.info("Employee instance updated and saved: %s", instance)

            # Update related User fields
            user_data = {key: validated_data[key] for key in validated_data if hasattr(instance.user, key)}
            logger.debug("User data to update: %s", user_data)
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()
            logger.info("User instance updated and saved: %s", instance.user)

            return instance
        else:
            logger.warning("Unauthorized attempt to update Employee data by user: %s", request_user)
            raise serializers.ValidationError({
                'authorization': 'You are not authorized to update this employee data.'
            })


    

    def get_entity(self, obj):
        return obj.entity.name if obj.entity else None

    def get_instance(self, obj):
        return obj.instance.name if obj.instance else None

    def get_unit(self, obj):
        return obj.unit.name if obj.unit else None
   