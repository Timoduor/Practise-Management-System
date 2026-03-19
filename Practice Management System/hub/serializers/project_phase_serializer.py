from rest_framework import serializers
from .base_serializer import SoftDeleteBaseSerializer
from hub.models.project import Project
from hub.models.project_phase import ProjectPhase
from core.models.employee import Employee
from core.serializers.employee_serializers import EmployeeSerializer
from .task_serializer import TaskSerializer


class ProjectPhaseSerializer(SoftDeleteBaseSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    tasks = TaskSerializer(many=True, read_only= True)

    members = EmployeeSerializer(many=True, read_only=True)
    member_ids = serializers.PrimaryKeyRelatedField(
        many=True,  queryset=Employee.objects.all(), source='phase_members', required=False
    )

    class Meta(SoftDeleteBaseSerializer.Meta):
        model = ProjectPhase
        fields = ['phase_id', 'phase_name', 'project', 'phase_description', 'start_date', 'end_date','members','member_ids', 'is_deleted', 'created_at', 'updated_at', 'tasks'] + SoftDeleteBaseSerializer.Meta.fields

    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("End date must be after the start date.")

        return data
    
    def create(self, validated_data):
        members = validated_data.pop('members', [])
        phase = ProjectPhase.objects.create(**validated_data)
        phase.members.set(members)  # Add members to the project
        return phase

    def update(self, instance, validated_data):
        members = validated_data.pop('members', [])
        instance = super().update(instance, validated_data)
        instance.members.set(members)  # Update the members of the project
        return instance
    
