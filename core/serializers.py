from typing import Any, Dict
from rest_framework_simplejwt.tokens import Token, RefreshToken
from .models import *
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
import string
from django.core.mail import send_mail
import secrets


class SoftDeleteMixin:
    def perform_soft_delete(self, instance):
        instance.delete()  # Call the soft delete method from the model

class UserSerializer(serializers.ModelSerializer, SoftDeleteMixin):

    employee_instance = serializers.PrimaryKeyRelatedField(queryset=Instance.objects.all(),  required=False)
    employee_entity = serializers.PrimaryKeyRelatedField(queryset=Entity.objects.all(),  required=False)
    employee_unit = serializers.PrimaryKeyRelatedField(queryset=Unit.objects.all(), required=False)

    instance_name = serializers.CharField(write_only=True, required=False)
    industry = serializers.CharField(write_only=True, required=False)
    class Meta:
        model = User
        fields = ['id','email','password', 'first_name', 'last_name', 'other_names', 'phone_number', 'address', 'dob', 'is_staff', 'is_superuser', 'is_active', 'employee_instance', 'employee_entity', 'employee_unit', 
                'instance_name', 'industry' ]
        extra_kwargs = {'password': {'write_only': True, 'required': False},
                    }
        
    def validate(self, data):
        # Get the values from the serializer data
        employee_instance = data.get('employee_instance')
        employee_entity = data.get('employee_entity')
        employee_unit = data.get('employee_unit')

        # Validate employee_entity against employee_instance
        if employee_entity and employee_instance:
            if employee_entity.instance != employee_instance:
                raise serializers.ValidationError({
                    'employee_entity': 'The selected entity must belong to the selected instance.'
                })

        # Validate employee_unit against employee_entity
        if employee_unit and employee_entity:
            if employee_unit.entity != employee_entity:
                raise serializers.ValidationError({
                    'employee_unit': 'The selected unit must belong to the selected entity.'
                })

        return data

    def create(self, validated_data):
        request_user = self.context['request'].user

        employee_instance = validated_data.pop('employee_instance', None) or getattr(request_user.employee_user, 'instance', None)
        employee_entity = validated_data.pop('employee_entity', None) or getattr(request_user.employee_user, 'entity', None)
        employee_unit = validated_data.pop('employee_unit', None) or getattr(request_user.employee_user, 'unit', None)
        
        # Instance name and Industry for the creation of an instance with the first user
        
        industry = validated_data.pop("industry", None)
        instance_name = validated_data.pop("instance_name", None)

        password = validated_data.get('password')

        #Actual creation of the user object
        user = User.objects.create(**validated_data)
        if(password):
            user.set_password(validated_data['password'])
        else:
            alphabet = string.ascii_letters + string.digits + string.punctuation
            random_password = ''.join(secrets.choice(alphabet) for i in range(12))
            user.set_password(random_password) 
            send_mail(
            subject='Your New Account Details',
            message=f'Hello {user.first_name},\n\nYour account has been created successfully. Your login password is: {random_password}\nPlease change your password after logging in for the first time.\n\nBest regards,\nYour Company',
            from_email='noreply@yourdomain.com',  # Replace with your from email address
            recipient_list=[user.email],
            fail_silently=False,
        )


         # Check if this is the first user for the given instance
        if employee_instance:
            if not Employee.objects.filter(instance=employee_instance).exists():
                user.is_staff = True
                user.save()

                # First user in the instance (Instance Admin flow)
                admin_type, created = AdminType.objects.get_or_create(name="INS")
                #Creating the instance Admin Object
                Admin.objects.create(
                    user=user,
                    admin_type=admin_type,
                    jurisdiction_content_type=ContentType.objects.get_for_model(Instance),
                    jurisdiction_object_id= employee_instance.id,
                    created_by=user,
                    last_updated_by=user
                )
            else:
                # Add as a regular user to the existing instance
                #Create the employee object
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
            # Create the instance if it's the first user and instance details are provided
            if instance_name and industry:
                user.is_staff = True  # Mark the first user as admin
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

class EmployeeSerializer(serializers.ModelSerializer, SoftDeleteMixin):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  # Use `user` field
    user_detail = UserSerializer(source='user', read_only=True)  # For nested serialization of user details if needed


    # user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    # user = UserSerializer(read_only =True)
    class Meta:
        model = Employee
        fields = ['id','user', 'user_detail', 'instance', 'entity', 'unit']

class AdminSerializer(serializers.ModelSerializer, SoftDeleteMixin):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    admin_type = serializers.SlugRelatedField(slug_field='name', queryset=AdminType.objects.all()) 

    class Meta:
        model = Admin
        fields = ['id','user', 'admin_type' ,'jurisdiction_content_type', 'jurisdiction_object_id',  ]


class UnitSerializer(serializers.ModelSerializer, SoftDeleteMixin):
    class Meta:
        model = Unit
        fields = ['id', 'name', 'unit_type', 'address', 'entity', 'is_deleted' ,'created_at', 'updated_at', 'last_updated_by', 'created_by',]


class EntitySerializer(serializers.ModelSerializer, SoftDeleteMixin):
    units = UnitSerializer(many=True, read_only= True)
    class Meta:
        model = Entity# instance = 
        fields = ['id','name' ,'entity_type', 'description', 'instance', 'parent_entity','is_deleted' ,'created_at', 'updated_at', 'last_updated_by', 'created_by', "units"]


class InstanceSerializer(serializers.ModelSerializer, SoftDeleteMixin):
    entities = EntitySerializer(many=True, read_only=True)

    class Meta:
        model = Instance
        fields = ['id' , 'name', 'code' ,'industry', 'is_deleted' ,'created_at', 'updated_at', 'last_updated_by', 'created_by', 'entities']
    

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):


        token = super().get_token(user)
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name

        return token
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed(detail ="User does not exist", code='user_does_not_exist')
        
        user = authenticate(email=email, password= password)

        if user is None:
            raise AuthenticationFailed(detail="Incorrect password", code='incorrect_password')
        return super().validate(attrs)