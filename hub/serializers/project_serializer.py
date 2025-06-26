from rest_framework import serializers
from .base_serializer import SoftDeleteBaseSerializer
from hub.models.project import Project
from hub.models.customer import Customer
from core.models.employee import Employee
from core.serializers.employee_serializers import EmployeeSerializer
from .project_phase_serializer import ProjectPhaseSerializer


class ProjectSerializer(SoftDeleteBaseSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    project_manager = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), required=False)
    members = EmployeeSerializer(many=True, read_only=True)
    member_ids = serializers.PrimaryKeyRelatedField(
        many=True,  queryset=Employee.objects.all(), source='members', required=False
    )
    phases = ProjectPhaseSerializer(many=True, read_only=True)

    class Meta(SoftDeleteBaseSerializer.Meta):
        model = Project
        fields = [
            'project_id', 'project_name', 'customer', 'project_description', 
            'start_date', 'end_date', 'instance', 'entity', 'unit', 'is_deleted', 'project_value',
            'created_at', 'updated_at', 'project_manager','members', 'member_ids', 'phases'
        ] + SoftDeleteBaseSerializer.Meta.fields

    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        # Get the project instance (for update operations) or entity instance (for create operations)
        project_instance = self.instance
        
        
        if project_instance:
            # For update operations, get the instance from the project
            project_instance = project_instance.entity.instance
        else:
            # For create operations, check if entity exists and has an instance
            entity = data.get('entity')
            if entity and hasattr(entity, 'instance'):
                project_instance = entity.instance
            else:
                raise serializers.ValidationError("Entity instance must be provided for project creation.")


        # project_instance = project_instance.entity.instance if project_instance else data['entity'].instance

        # Validate that all employees in 'member_ids' belong to the same instance as the project
        employees = data.get('members', [])
        for employee in employees:
            if employee.instance != project_instance:
                raise serializers.ValidationError(
                    f"Employee {employee.user} does not belong to the same instance as the project."
                )
        #Check that end date occurs after the start date
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("End date must be after the start date.")

        entity = data.get('entity')
        unit = data.get('unit')

        #Check if input unit belongs to the input entity
        if unit and entity and unit.entity != entity:
            raise serializers.ValidationError({
                'unit': 'The selected unit must belong to the selected entity.'
            })

        return data

    def create(self, validated_data):
        members = validated_data.pop('members', [])
        project = Project.objects.create(**validated_data)
        project.members.set(members)  # Add members to the project
        return project

    def update(self, instance, validated_data):
        members = validated_data.pop('members', [])
        instance = super().update(instance, validated_data)
        instance.members.set(members)  # Update the members of the project
        return instance

