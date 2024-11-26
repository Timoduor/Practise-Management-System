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

import logging
import string, secrets
from django.core.mail import send_mail

logger = logging.getLogger(__name__)
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
        logger.debug("Creating a new user with validated data: %s", validated_data)
        
        request_user = self.context['request'].user
        employee_instance = validated_data.pop('employee_instance', None)
        employee_entity = validated_data.pop('employee_entity', None)
        employee_unit = validated_data.pop('employee_unit', None)
        if request_user.is_authenticated and hasattr(request_user, 'employee_user'):
            logger.debug("Authenticated request user found with employee_user attribute.")

        else:
            logger.debug("No authenticated request user or employee_user attribute found.")


        industry = validated_data.pop("industry", None)
        instance_name = validated_data.pop("instance_name", None)
        password = validated_data.get('password')

        # Create user
        user = User.objects.create(**validated_data)
        logger.info("User %s created successfully", user.email)

        if password:
            logger.debug("Setting user password from provided data.")
            user.set_password(validated_data['password'])
        else:
            # Generate and send password
            logger.debug("No password provided, generating random password.")
            alphabet = string.ascii_letters + string.digits + string.punctuation
            random_password = ''.join(secrets.choice(alphabet) for i in range(12))
            user.set_password(random_password)
            try:
                send_mail(
                    subject='Your New Account Details',
                    message=f'Hello {user.first_name},\n\nYour account has been created successfully. Your login password is: {random_password}\nPlease change your password after logging in for the first time.\n\nBest regards,\nYour Company',
                    from_email='noreply@yourdomain.com',  # Replace with actual sender address
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                logger.info("Password email sent to %s", user.email)
            except Exception as e:
                logger.error("Failed to send password email to %s: %s", user.email, e)

        #We're fine up to here

        if instance_name and industry:
            logger.debug("Instance creation data provided, creating new instance.")
            user.is_staff = True
            user.save()

            instance = Instance.objects.create(
                    name=instance_name,
                    code=f"{instance_name[:3].upper()}{User.objects.count()}"[:15],
                    industry=industry,
                    created_by=user,
                    last_updated_by=user
            )
            logger.info("Instance %s created for first user %s", instance_name, user.email)

            admin_type, created = AdminType.objects.get_or_create(name="INS")
            Admin.objects.create(
                  user=user,
                    admin_type=admin_type,
                    jurisdiction_content_type=ContentType.objects.get_for_model(Instance),
                    jurisdiction_object_id=instance.id,
                    created_by=user,
                    last_updated_by=user
                )
            logger.info("Admin record created for user %s as instance admin", user.email)

            Employee.objects.create(
                    user=user,
                    instance=instance,
                    entity=None,
                    unit=None
            )
            logger.info("Employee record created for instance admin user %s", user.email)
        else:
            employee_instance = employee_instance or getattr(request_user.employee_user, 'instance', None)
            # employee_entity = validated_data.pop('employee_entity', None) 
            # employee_unit = validated_data.pop('employee_unit', None) 

            logger.info("The instance for this request is %s", employee_instance)
            logger.info("The ENTITY for this request is %s", employee_entity)
            logger.info("The instance for this request is %s", employee_unit)

            if employee_instance:
                logger.debug("Employee instance provided: %s", employee_instance)
                if not Employee.objects.filter(instance=employee_instance).exists():
                    logger.debug("No existing employees for this instance; setting user as instance admin.")
                    user.is_staff = True
                    user.save()

                    admin_type, created = AdminType.objects.get_or_create(name="INS")
                    Admin.objects.create(
                        user=user,
                        admin_type=admin_type,
                        jurisdiction_content_type=ContentType.objects.get_for_model(Instance),
                        jurisdiction_object_id=employee_instance.id,
                        created_by=user,
                        last_updated_by=user
                    )
                    logger.info("Admin record created for user %s as instance admin", user.email)
                else:
                    if self.context['request'].user.is_staff:
                        logger.debug("Staff user creating a new employee for instance.")
                        user.save()
                        Employee.objects.create(
                            user=user,
                            instance=employee_instance,
                            entity=employee_entity,
                            unit=employee_unit
                        )
                        logger.info("Employee record created for user %s", user.email)
                    else:
                        logger.warning("Unauthorized attempt to create user by non-staff user %s", request_user.email)
                        raise serializers.ValidationError({
                            'authorization': 'Only instance admins can create new users.'
                        })

        return user


    def update(self, instance, validated_data):
        request_user = self.context['request'].user
        logger.info("Updating user instance. Request user: %s", request_user)

        # Ensure the user is authorized to update
        if not (request_user.is_staff or request_user == instance):
            logger.warning("Unauthorized attempt to update user data by: %s", request_user)
            raise serializers.ValidationError({
                'authorization': 'You are not authorized to update this user data.'
            })

        # Extract employee-related fields from validated data
        employee_instance = validated_data.pop('employee_instance', None)
        employee_entity = validated_data.pop('employee_entity', None)
        employee_unit = validated_data.pop('employee_unit', None)

        logger.debug("Validated data before applying updates: %s", validated_data)
        logger.debug("Employee-related fields - instance: %s, entity: %s, unit: %s",
                    employee_instance, employee_entity, employee_unit)

        # Update user fields
        user_fields = {key: value for key, value in validated_data.items() if hasattr(instance, key)}
        for attr, value in user_fields.items():
            setattr(instance, attr, value)

        logger.debug("User fields updated for instance: %s", user_fields)

        # Save user updates
        instance.save()
        logger.info("User instance updated and saved: %s", instance)

        # Handle employee instance updates if the user is an employee
        if hasattr(instance, 'employee_user'):
            employee = instance.employee_user

            # Update employee fields if provided
            if employee_instance:
                employee.instance = employee_instance
                logger.info("Updated employee instance field to: %s", employee_instance)
            if employee_entity:
                # if employee_entity.instance != employee_instance:
                #     logger.info("Entity Instance")
                #     logger.warning("Employee entity does not belong to the provided instance.")
                #     raise serializers.ValidationError({
                #         'employee_entity': 'The selected entity must belong to the selected instance.'
                #     })
                employee.entity = employee_entity
                logger.info("Updated employee entity field to: %s", employee_entity)
            if employee_unit:
                # if employee_unit.entity != employee_entity:
                #     logger.warning("Employee unit does not belong to the provided entity.")
                #     raise serializers.ValidationError({
                #         'employee_unit': 'The selected unit must belong to the selected entity.'
                #     })
                employee.unit = employee_unit
                logger.info("Updated employee unit field to: %s", employee_unit)

            # Save employee updates
            employee.save()
            logger.info("Employee data updated and saved for user: %s", instance)

        return instance
