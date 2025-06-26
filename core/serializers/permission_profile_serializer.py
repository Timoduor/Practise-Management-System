# core/serializers/permission_profile_serializer.py
from rest_framework import serializers
from core.models.permission_profile import PermissionProfile, Permission

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'code', 'description']
        ref_name = "PermissionProfilePermission"

class PermissionProfileSerializer(serializers.ModelSerializer):
    permission_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Permission.objects.all(),
        write_only=True
    )
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = PermissionProfile
        fields = ['id', 'organisation', 'name', 'description', 'permission_ids', 'permissions']
        read_only_fields = ['organisation']

    def create(self, validated_data):
        permissions = validated_data.pop('permission_ids', [])
        profile = PermissionProfile.objects.create(**validated_data)
        profile.permissions.set(permissions)
        return profile

    def update(self, instance, validated_data):
        permissions = validated_data.pop('permission_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if permissions is not None:
            instance.permissions.set(permissions)
        instance.save()
        return instance



