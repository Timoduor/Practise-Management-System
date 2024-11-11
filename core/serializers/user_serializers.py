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

import string, secrets
from django.core.mail import send_mail

# Serializer for the User model with additional employee-related fields
class UserSerializer(serializers.ModelSerializer, SoftDeleteMixin):
    # Fields for linking employee to instance, entity, and unit
    employee_instance = serializers.PrimaryKeyRelatedField(queryset=Instance.objects.all(), required=False)
    employee_entity = serializers.PrimaryKeyRelatedField(queryset=Entity.objects.all(), required=False)
    employee_unit = serializers.PrimaryKeyRelatedField(queryset=Unit.objects.all(), required=False)

    # Write-only fields for creating an instance with the user
    instance_name = serializers.CharField(write_only=True, required=False)
    industry = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        # Define all relevant fields for User model
        fields = [
            'id', 'email', 'password', 'first_name', 'last_name', 'other_names', 'phone_number', 
            'address', 'dob', 'is_staff', 'is_superuser', 'is_active', 'employee_instance', 
            'employee_entity', 'employee_unit', 'instance_name', 'industry'
        ]
        extra_kwargs = {'password': {'write_only': True, 'required': False}}

    def validate(self, data):
        # Validate instance and entity relationships
        employee_instance = data.get('employee_instance')
        employee_entity = data.get('employee_entity')
        employee_unit = data.get('employee_unit')

        if employee_entity and employee_instance:
            if employee_entity.instance != employee_instance:
                raise serializers.ValidationError({
                    'employee_entity': 'The selected entity must belong to the selected instance.'
                })

        if employee_unit and employee_entity:
            if employee_unit.entity != employee_entity:
                raise serializers.ValidationError({
                    'employee_unit': 'The selected unit must belong to the selected entity.'
                })

        return data

    def create(self, validated_data):
        # Context for the current request user
        request_user = self.context['request'].user

        # Retrieve employee fields from validated data or use default from request user
        if request_user.is_authenticated and hasattr(request_user, 'employee_user'):
            employee_instance = validated_data.pop('employee_instance', None) or getattr(request_user.employee_user, 'instance', None)
            employee_entity = validated_data.pop('employee_entity', None) or getattr(request_user.employee_user, 'entity', None)
            employee_unit = validated_data.pop('employee_unit', None) or getattr(request_user.employee_user, 'unit', None)
        else:
            employee_instance = None
            employee_entity = None
            employee_unit = None

        # Retrieve optional instance data for the first user in an instance
        industry = validated_data.pop("industry", None)
        instance_name = validated_data.pop("instance_name", None)
        password = validated_data.get('password')

        # Create the user object
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(validated_data['password'])
        else:
            # Generate a random password and send it to the user via email
            alphabet = string.ascii_letters + string.digits + string.punctuation
            random_password = ''.join(secrets.choice(alphabet) for i in range(12))
            user.set_password(random_password)
            send_mail(
                subject='Your New Account Details',
                message=f'Hello {user.first_name},\n\nYour account has been created successfully. Your login password is: {random_password}\nPlease change your password after logging in for the first time.\n\nBest regards,\nYour Company',
                from_email='noreply@yourdomain.com',  # Replace with actual sender address
                recipient_list=[user.email],
                fail_silently=False,
            )

        # Check if this user is the first user for the given instance
        if employee_instance:
            if not Employee.objects.filter(instance=employee_instance).exists():
                # Assign admin privileges for the first user in an instance
                user.is_staff = True
                user.save()

                # Assign instance admin type and create Admin object
                admin_type, created = AdminType.objects.get_or_create(name="INS")
                Admin.objects.create(
                    user=user,
                    admin_type=admin_type,
                    jurisdiction_content_type=ContentType.objects.get_for_model(Instance),
                    jurisdiction_object_id=employee_instance.id,
                    created_by=user,
                    last_updated_by=user
                )
            else:
                # For regular users added by instance admin
                if self.context['request'].user.is_staff:
                    user.save()
                    Employee.objects.create(
                        user=user,
                        instance=employee_instance,
                        entity=employee_entity,
                        unit=employee_unit
                    )
                else:
                    raise serializers.ValidationError({
                        'authorization': 'Only instance admins can create new users.'
                    })
        else:
            # Create a new instance if it’s the first user registration with instance details
            if instance_name and industry:
                user.is_staff = True  # First user as instance admin
                user.save()

                instance = Instance.objects.create(
                    name=instance_name,
                    code=f"{instance_name[:3].upper()}{User.objects.count()}"[:15],
                    industry=industry,
                    created_by=user,
                    last_updated_by=user
                )

                # Make the first user the instance admin
                admin_type, created = AdminType.objects.get_or_create(name="INS")
                Admin.objects.create(
                    user=user,
                    admin_type=admin_type,
                    jurisdiction_content_type=ContentType.objects.get_for_model(Instance),
                    jurisdiction_object_id=instance.id,
                    created_by=user,
                    last_updated_by=user
                )

                # Create an Employee record for the instance admin
                Employee.objects.create(
                    user=user,
                    instance=instance,
                    entity=None,
                    unit=None
                )
            else:
                raise serializers.ValidationError({
                    'instance': 'Instance details are required for the first user registration.'
                })

        return user

