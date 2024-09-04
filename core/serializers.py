from .models import *
from rest_framework import serializers


class SoftDeleteMixin:
    def perform_soft_delete(self, instance):
        instance.delete()  # Call the soft delete method from the model
class UserSerializer(serializers.ModelSerializer, SoftDeleteMixin):
    class Meta:
        model = User
        fields = ['id','email','password', 'first_name', 'last_name', 'other_names', 'phone_number', 'address', 'dob', 'is_staff', 'is_superuser', 'is_active', 'employee_instance', 'employee_entity', 'employee_unit' ]
        extra_kwargs = {'password': {'write_only': True},
                    }
    
    def create(self, validated_data):
        admin_data = validated_data.pop('admin',None)
        employee_data = validated_data.pop('employee', None)
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()

        if user.is_staff:
            admin_type, created = AdminType.objects.get_or_create(name="INS")
            Admin.objects.create(user=user, admin_type=admin_type)

        if 'employee_instance' in validated_data:
            Employee.objects.create(
                user = user,
                instance = validated_data['employee_instance'],
                entity = validated_data.get("employee_entity"),
                unit = validated_data.get("employee_unit")

            )
        return user

class EmployeeSerializer(serializers.ModelSerializer, SoftDeleteMixin):
    user = UserSerializer()

    class Meta:
        model = Employee
        fields = ['id','user', 'instance', 'entity', 'unit']

class AdminSerializer(serializers.ModelSerializer, SoftDeleteMixin):
    user = UserSerializer()
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
    
