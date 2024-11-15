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

    def update(self, instance, validated_data):
        # Get the request user from the context
        request_user = self.context['request'].user
        print(request_user)

        # Check if the request user is either an admin or the user linked to this Employee instance
        if request_user.is_staff or request_user == instance.user:
            # Pop fields specific to Employee relationships
            employee_instance = validated_data.pop('employee_instance', None)
            print(employee_instance)
            employee_entity = validated_data.pop('employee_entity', None)
            print(employee_entity)
            employee_unit = validated_data.pop('employee_unit', None)
            print(employee_unit)

            print(instance)
            print("employee_entity", employee_entity)
            print("unit", employee_unit)
            print(validated_data)

            # Update Employee-related fields if provided
            if employee_instance:
                instance.instance = employee_instance
                print("Instance", instance)
            if employee_entity:
                instance.entity = employee_entity
                print("Entity", instance.entity)
            if employee_unit:
                instance.unit = employee_unit
                print("Unit", instance.unit)
            # Save changes to Employee instance
            instance.save()
            print(instance.save)

            # Update User-related fields for the linked user object
            user_data = {key: validated_data[key] for key in validated_data if hasattr(instance.user, key)}
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()

            # Return updated Employee instance
            return instance
        else:
            # Raise error if not authorized to perform the update
            raise serializers.ValidationError({
                'authorization': 'You are not authorized to update this employee data.'
            })
    

    def get_entity(self, obj):
        return obj.entity.name if obj.entity else None

    def get_instance(self, obj):
        return obj.instance.name if obj.instance else None

    def get_unit(self, obj):
        return obj.unit.name if obj.unit else None
   