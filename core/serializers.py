from .models import *
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','email', 'first_name', 'last_name', 'other_names', 'phone_number', 'address', 'dob' ]
        extra_kwargs = {'password': {'write_only': True}}

class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Employee
        fields = ['id','user', 'instance', 'entity', 'unit']

class AdminSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    admin_type = serializers.SlugRelatedField(slug_field='name', queryset=AdminType.objects.all()) 

    class Meta:
        model = Admin
        fields = ['id','user', 'admin_type' ,'jurisdiction_content_type', 'jurisdiction_content_id',  ]
