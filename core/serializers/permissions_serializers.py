# core/serializers/permission.py
from rest_framework import serializers
from core.models.permission_profile import Permission

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'profile', 'code', 'description']
        ref_name = "OrgLevelPermission" 
