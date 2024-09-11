from rest_framework import serializers
from core.models import User  
from .models import Customer, Contact, Sales, Project, Task, Invoice, ProjectPhase, WorkEntries, Absence, Expense, LeaveType

class CustomerSerializer(serializers.ModelSerializer):
    contacts = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    sales = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Customer
        fields = ['customer_id', 'customer_name', 'customer_email', 'customer_phone', 'customer_address', 'entity', 'unit', 'is_deleted', 'created_at', 'updated_at', 'contacts', 'sales']

    def validate(self, data):
        entity = data.get('entity')
        unit = data.get('unit')

        if unit and entity:
            if unit.entity != entity:
                raise serializers.ValidationError({
                    'unit': 'The selected unit must belong to the selected entity.'
                })
        
        return data


class ContactSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())

    class Meta:
        model = Contact
        fields = ['contact_id', 'contact_name', 'contact_email', 'contact_phone', 'contact_address', 'role', 'customer', 'is_deleted', 'created_at', 'updated_at']


class SalesSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    project_manager = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

    class Meta:
        model = Sales
        fields = [
            'sales_id', 'sales_name', 'sales_description', 'project_value', 
            'expected_order_date', 'sales_status', 'customer', 'project_manager', 
            'created_by', 'entity', 'unit', 'is_deleted', 'created_at', 'updated_at'
        ]

    def validate(self, data):
        project_manager = data.get('project_manager')
        entity = data.get('entity')

        # Check if the project manager belongs to the same instance as the sale's entity
        if project_manager and entity:
            if project_manager.employee_entity != entity:
                raise serializers.ValidationError({
                    'project_manager': 'The selected project manager must belong to the same entity as the sale.'
                })

        return data


class ProjectSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())

    class Meta:
        model = Project
        fields = ['project_id', 'project_name', 'customer', 'project_description', 'start_date', 'end_date', 'entity', 'unit', 'is_deleted', 'created_at', 'updated_at']

    def validate(self, data):
        entity = data.get('entity')
        unit = data.get('unit')

        if unit and entity:
            if unit.entity != entity:
                raise serializers.ValidationError({
                    'unit': 'The selected unit must belong to the selected entity.'
                })

        return data


class ProjectPhaseSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())

    class Meta:
        model = ProjectPhase
        fields = ['phase_id', 'phase_name', 'project', 'phase_description', 'start_date', 'end_date', 'is_deleted', 'created_at', 'updated_at']

    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        # Ensure that the start date is before the end date
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError({
                'end_date': 'End date must be after the start date.'
            })

        return data


class TaskSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    assigned_to = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

    class Meta:
        model = Task
        fields = ['task_id', 'task_name', 'project', 'assigned_to', 'action_type', 'start_date', 'due_date', 'task_description', 'task_status', 'entity', 'unit', 'is_deleted', 'created_at', 'updated_at']

    def validate(self, data):
        project = data.get('project')
        entity = data.get('entity')
        unit = data.get('unit')

        if unit and entity:
            if unit.entity != entity:
                raise serializers.ValidationError({
                    'unit': 'The selected unit must belong to the selected entity.'
                })

        # Ensure the project's entity matches the task's entity
        if project and entity:
            if project.entity != entity:
                raise serializers.ValidationError({
                    'entity': 'The task must belong to the same entity as the project.'
                })

        return data


class WorkEntriesSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    phase = serializers.PrimaryKeyRelatedField(queryset=ProjectPhase.objects.all())
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all())

    class Meta:
        model = WorkEntries
        fields = ['work_entries_id', 'user', 'date', 'start_time', 'end_time', 'description', 'project', 'phase', 'task', 'task_type', 'is_deleted', 'created_at', 'updated_at']

    def validate(self, data):
        project = data.get('project')
        phase = data.get('phase')
        task = data.get('task')

        # Ensure the phase belongs to the correct project
        if phase and project:
            if phase.project != project:
                raise serializers.ValidationError({
                    'phase': 'The selected phase does not belong to the selected project.'
                })

        # Ensure the task belongs to the correct phase
        if task and phase:
            if task.phase != phase:
                raise serializers.ValidationError({
                    'task': 'The selected task does not belong to the selected phase.'
                })

        return data


class AbsenceSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), required=False)
    leave_type = serializers.PrimaryKeyRelatedField(queryset=LeaveType.objects.all(), required=False)

    class Meta:
        model = Absence
        fields = ['absence_id', 'user', 'absence_date', 'start_time', 'end_time', 'absence_description', 'project', 'leave_type', 'is_deleted', 'created_at', 'updated_at']

    def validate(self, data):
        project = data.get('project')
        leave_type = data.get('leave_type')

        # Optionally, if a project is selected, ensure it belongs to a valid project
        if project:
            if not Project.objects.filter(pk=project.id).exists():
                raise serializers.ValidationError({
                    'project': 'The selected project does not exist.'
                })

        return data


class ExpenseSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    phase = serializers.PrimaryKeyRelatedField(queryset=ProjectPhase.objects.all())
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all())

    class Meta:
        model = Expense
        fields = ['expense_id', 'user', 'project', 'phase', 'task', 'date', 'value', 'description', 'is_deleted', 'created_at', 'updated_at']

    def validate(self, data):
        project = data.get('project')
        phase = data.get('phase')
        task = data.get('task')

        # Ensure the phase belongs to the correct project
        if phase and project:
            if phase.project != project:
                raise serializers.ValidationError({
                    'phase': 'The selected phase does not belong to the selected project.'
                })

        # Ensure the task belongs to the correct phase
        if task and phase:
            if task.phase != phase:
                raise serializers.ValidationError({
                    'task': 'The selected task does not belong to the selected phase.'
                })

        return data


class InvoiceSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), required=False)
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(), required=False)

    class Meta:
        model = Invoice
        fields = ['invoice_id', 'project', 'customer', 'invoice_amount', 'invoice_date', 'paid_status', 'entity', 'unit', 'is_deleted', 'created_at', 'updated_at']

    def validate(self, data):
        project = data.get('project')
        entity = data.get('entity')
        unit = data.get('unit')

        if unit and entity:
            if unit.entity != entity:
                raise serializers.ValidationError({
                    'unit': 'The selected unit must belong to the selected entity.'
                })

        # Ensure the project's entity matches the invoice's entity
        if project and entity:
            if project.entity != entity:
                raise serializers.ValidationError({
                    'entity': 'The invoice must belong to the same entity as the project.'
                })

        return data