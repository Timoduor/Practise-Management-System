from rest_framework import serializers
from core.models.user import User
from core.models.admin import Admin
from core.models.employee import Employee
from core.models.admin_type import AdminType
from core.models.instance import Instance
from core.models.entity import Entity
from core.models.unit import Unit
from .base_serializers import BaseModelSerializer
from django.contrib.contenttypes.models import ContentType
import logging
import string
import secrets
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

class UserSerializer(BaseModelSerializer):
    """
    Main serializer for User model with comprehensive functionality
    """
    # Computed fields
    full_name = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    
    # Employee relationship fields
    employee_instance = serializers.PrimaryKeyRelatedField(
        queryset=Instance.objects.all(),
        required=False,
        allow_null=True
    )
    employee_entity = serializers.PrimaryKeyRelatedField(
        queryset=Entity.objects.all(),
        required=False,
        allow_null=True
    )
    employee_unit = serializers.PrimaryKeyRelatedField(
        queryset=Unit.objects.all(),
        required=False,
        allow_null=True
    )

    # Instance creation fields
    instance_name = serializers.CharField(write_only=True, required=False)
    industry = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'password',
            'first_name',
            'last_name',
            'other_names',
            'full_name',
            'phone_number',
            'address',
            'dob',
            'is_staff',
            'is_superuser',
            'is_active',
            'roles',
            'employee_instance',
            'employee_entity',
            'employee_unit',
            'instance_name',
            'industry',
            'created_at',
            'updated_at',
            'last_updated_by',
            'created_by',
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
        read_only_fields = [
            'id',
            'is_superuser',
            'created_at',
            'updated_at',
            'created_by',
            'last_updated_by',
        ]

    def get_full_name(self, obj):
        """Generate full name including other names if available"""
        names = [obj.first_name, obj.last_name]
        if obj.other_names:
            names.insert(1, obj.other_names)
        return " ".join(filter(None, names))

    def get_roles(self, obj):
        """Get user roles and jurisdictions"""
        roles = []
        
        if obj.is_superuser:
            roles.append({
                'role': 'Superuser',
                'jurisdiction': 'System-wide'
            })
            
        if hasattr(obj, 'admin_user'):
            admin = obj.admin_user
            roles.append({
                'role': f'{admin.admin_type.name} Administrator',
                'jurisdiction': str(admin.get_jurisdiction())
            })
            
        if hasattr(obj, 'employee_user'):
            employee = obj.employee_user
            role = {
                'role': 'Employee',
                'instance': str(employee.instance),
            }
            if employee.entity:
                role['entity'] = str(employee.entity)
            if employee.unit:
                role['unit'] = str(employee.unit)
            roles.append(role)
            
        return roles

    def validate_email(self, value):
        """Validate email format and uniqueness"""
        value = value.lower().strip()
        if User.objects.filter(email__iexact=value).exists():
            if not self.instance or self.instance.email.lower() != value:
                raise serializers.ValidationError(
                    "A user with this email already exists."
                )
        return value

    def validate(self, data):
        """Validate relationships and data integrity"""
        # Validate instance and entity relationships
        employee_instance = data.get('employee_instance')
        employee_entity = data.get('employee_entity')
        employee_unit = data.get('employee_unit')

        if employee_entity and employee_instance:
            if employee_entity.instance != employee_instance:
                raise serializers.ValidationError({
                    'employee_entity': 'Entity must belong to the selected instance.'
                })

        if employee_unit and employee_entity:
            if employee_unit.entity != employee_entity:
                raise serializers.ValidationError({
                    'employee_unit': 'Unit must belong to the selected entity.'
                })

        # Validate required name fields
        if not data.get('first_name', self.instance and self.instance.first_name):
            raise serializers.ValidationError({
                'first_name': 'First name is required.'
            })
            
        if not data.get('last_name', self.instance and self.instance.last_name):
            raise serializers.ValidationError({
                'last_name': 'Last name is required.'
            })

        return data

    def _generate_and_send_password(self, user):
        """Generate random password and send to user"""
        alphabet = string.ascii_letters + string.digits + string.punctuation
        random_password = ''.join(secrets.choice(alphabet) for i in range(12))
        user.set_password(random_password)
        
        try:
            send_mail(
                subject='Your Account Details',
                message=f'''Hello {user.first_name},

Your account has been created successfully.
Email: {user.email}
Temporary Password: {random_password}

Please change your password after logging in.

Best regards,
System Administrator''',
                from_email='noreply@yourdomain.com',
                recipient_list=[user.email],
                fail_silently=False,
            )
            logger.info(f"Password email sent to {user.email}")
        except Exception as e:
            logger.error(f"Failed to send password email to {user.email}: {str(e)}")
            raise serializers.ValidationError({
                'email': 'Failed to send account details email.'
            })

    def create(self, validated_data):
        """Create user with proper role assignment"""
        logger.info(f"Creating new user with data: {validated_data}")
        
        # Extract related fields
        employee_instance = validated_data.pop('employee_instance', None)
        employee_entity = validated_data.pop('employee_entity', None)
        employee_unit = validated_data.pop('employee_unit', None)
        instance_name = validated_data.pop('instance_name', None)
        industry = validated_data.pop('industry', None)
        
        # Create user
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        
        if password:
            user.set_password(password)
        else:
            self._generate_and_send_password(user)
        
        # Handle instance creation case
        if instance_name and industry:
            self._create_instance_admin(user, instance_name, industry)
        # Handle employee creation case
        elif employee_instance:
            self._create_employee(user, employee_instance, employee_entity, employee_unit)
            
        user.save()
        return user

    def _create_instance_admin(self, user, instance_name, industry):
        """Create instance and set user as admin"""
        instance = Instance.objects.create(
            name=instance_name,
            industry=industry,
            created_by=user,
            last_updated_by=user
        )
        
        admin_type = AdminType.objects.get_or_create(
            name="INS",
            defaults={
                "description": "Instance Administrator",
                "created_by": user,
                "last_updated_by": user
            }
        )[0]
        
        Admin.objects.create(
            user=user,
            admin_type=admin_type,
            jurisdiction_content_type=ContentType.objects.get_for_model(Instance),
            jurisdiction_object_id=instance.id,
            created_by=user,
            last_updated_by=user
        )
        
        Employee.objects.create(
            user=user,
            instance=instance
        )
        
        user.is_staff = True

    def _create_employee(self, user, instance, entity=None, unit=None):
        """Create employee record"""
        Employee.objects.create(
            user=user,
            instance=instance,
            entity=entity,
            unit=unit
        )

    def update(self, instance, validated_data):
        """Update user and related records"""
        # Extract related fields
        employee_instance = validated_data.pop('employee_instance', None)
        employee_entity = validated_data.pop('employee_entity', None)
        employee_unit = validated_data.pop('employee_unit', None)
        
        # Update password if provided
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
            
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        # Update employee if exists
        if hasattr(instance, 'employee_user'):
            employee = instance.employee_user
            if employee_instance:
                employee.instance = employee_instance
            if employee_entity:
                employee.entity = employee_entity
            if employee_unit:
                employee.unit = employee_unit
            employee.save()
            
        instance.save()
        return instance


class UserListSerializer(UserSerializer):
    """Simplified serializer for list views"""
    class Meta(UserSerializer.Meta):
        fields = [
            'id',
            'email',
            'full_name',
            'roles',
            'is_active',
        ]


class UserSimpleSerializer(serializers.ModelSerializer):
    """Minimal serializer for nested relationships"""
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
        ]