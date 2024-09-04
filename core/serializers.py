from .models import *
from rest_framework import serializers


class SoftDeleteMixin:
    def perform_soft_delete(self, instance):
        instance.delete()  # Call the soft delete method from the model
class UserSerializer(serializers.ModelSerializer, SoftDeleteMixin):
    class Meta:
        model = User
        fields = ['id','email','password', 'first_name', 'last_name', 'other_names', 'phone_number', 'address', 'dob', 'is_staff', 'is_superuser', 'is_active' ]
        extra_kwargs = {'password': {'write_only': True}}

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
        fields = ['id','user', 'admin_type' ,'jurisdiction_content_type', 'jurisdiction_content_id',  ]
