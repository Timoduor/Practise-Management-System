from rest_framework_simplejwt.tokens import Token
from .models import *
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class SoftDeleteMixin:
    def perform_soft_delete(self, instance):
        instance.delete()  # Call the soft delete method from the model

class UserSerializer(serializers.ModelSerializer, SoftDeleteMixin):

    employee_instance = serializers.PrimaryKeyRelatedField(queryset=Instance.objects.all(),  required=False)
    employee_entity = serializers.PrimaryKeyRelatedField(queryset=Entity.objects.all(),  required=False)
    employee_unit = serializers.PrimaryKeyRelatedField(queryset=Unit.objects.all(), required=False)
    class Meta:
        model = User
        fields = ['id','email','password', 'first_name', 'last_name', 'other_names', 'phone_number', 'address', 'dob', 'is_staff', 'is_superuser', 'is_active', 'employee_instance', 'employee_entity', 'employee_unit' ]
        extra_kwargs = {'password': {'write_only': True},
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
        employee_instance = validated_data.pop('employee_instance', None)
        employee_entity = validated_data.pop('employee_entity', None)
        employee_unit = validated_data.pop('employee_unit', None)
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()

        if user.is_staff:
            admin_type, created = AdminType.objects.get_or_create(name="INS")
            Admin.objects.create(user=user, admin_type=admin_type)

        if 'employee_instance' in validated_data:
            Employee.objects.create(
                user = user,
                instance = employee_instance,
                entity = employee_entity,
                unit = employee_unit

            )
        return user

class EmployeeSerializer(serializers.ModelSerializer, SoftDeleteMixin):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    class Meta:
        model = Employee
        fields = ['id','user', 'instance', 'entity', 'unit']

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