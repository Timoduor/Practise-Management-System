# Import necessary modules for typing, token management, and authentication
from typing import Any, Dict
from rest_framework_simplejwt.tokens import Token, RefreshToken
from .models import *  # Import all models from the current app
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
import string
from django.core.mail import send_mail
import secrets

# Mixin class to enable soft delete functionality in serializers
class SoftDeleteMixin:
    def perform_soft_delete(self, instance):
        # Call the soft delete method defined in the model
        instance.delete()

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



# Serializer for Employee model, including nested UserSerializer for user details
class EmployeeSerializer(serializers.ModelSerializer, SoftDeleteMixin):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  # Use `user` field
    user_detail = UserSerializer(source='user', read_only=True)  # Nested serialization for user details

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
            employee_entity = validated_data.pop('employee_entity', None)
            employee_unit = validated_data.pop('employee_unit', None)

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
                print("Entity", entity)
            if employee_unit:
                instance.unit = employee_unit
                print("Unit", unit)
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


# Serializer for Unit model with SoftDeleteMixin
class UnitSerializer(serializers.ModelSerializer, SoftDeleteMixin):
    class Meta:
        model = Unit
        # Define fields for Unit model
        fields = [
            'id', 'name', 'unit_type', 'address', 'entity', 'is_deleted', 'created_at', 
            'updated_at', 'last_updated_by', 'created_by'
        ]

# Serializer for Entity model with nested UnitSerializer for related units
class EntitySerializer(serializers.ModelSerializer, SoftDeleteMixin):
    units = UnitSerializer(many=True, read_only=True)  # Nested serializer for units within an entity

    class Meta:
        model = Entity
        fields = [
            'id', 'name', 'entity_type', 'description', 'instance', 'parent_entity', 'is_deleted', 
            'created_at', 'updated_at', 'last_updated_by', 'created_by', "units"
        ]

    def create(self, validated_data):
        user = self.context["request"]. user
        validated_data['instance'] = user.employee_user.instance 

        return super().create(validated_data)

# Serializer for Instance model with nested EntitySerializer for related entities
class InstanceSerializer(serializers.ModelSerializer, SoftDeleteMixin):
    entities = EntitySerializer(many=True, read_only=True)  # Nested serializer for entities within an instance

    class Meta:
        model = Instance
        fields = [
            'id', 'name', 'code', 'industry', 'is_deleted', 'created_at', 
            'updated_at', 'last_updated_by', 'created_by', 'entities'
        ]

# Custom TokenObtainPairSerializer to add custom claims in JWT tokens
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        # Get token from the superclass and add custom claims
        token = super().get_token(user)
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        return token

    def validate(self, attrs):
        # Override validate to provide custom authentication error handling
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            user = User.objects.get(email=email)  # Check if user exists
        except User.DoesNotExist:
            raise AuthenticationFailed(detail="User does not exist", code='user_does_not_exist')

        user = authenticate(email=email, password=password)  # Authenticate user

        if user is None:
            raise AuthenticationFailed(detail="Incorrect password", code='incorrect_password')
        return super().validate(attrs)  # Call superclass validate method
