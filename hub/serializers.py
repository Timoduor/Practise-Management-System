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
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("End date must be after the start date.")

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

        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("End date must be after the start date.")

        return data


class TaskSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    assigned_to = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

    class Meta:
        model = Task
        fields = ['task_id', 'task_name', 'project', 'phase', 'assigned_to', 'start_date', 'due_date', 'task_description', 'task_status', 'is_deleted', 'created_at', 'updated_at']

    def validate(self, data):
        start_date = data.get('start_date')
        due_date = data.get('due_date')

        if start_date and due_date and start_date > due_date:
            raise serializers.ValidationError("Due date must be after the start date.")

        project = data.get('project')
        phase = data.get('phase')

        if phase and phase.project != project:
            raise serializers.ValidationError("The phase must belong to the selected project.")

        return data


class WorkEntriesSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    phase = serializers.PrimaryKeyRelatedField(queryset=ProjectPhase.objects.all())
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all())

    class Meta:
        model = WorkEntries
        fields = ['work_entries_id', 'user', 'date', 'start_time', 'end_time', 'description', 'project', 'phase', 'task', 'task_type', 'is_deleted', 'created_at', 'updated_at']

    def validate(self, data):
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        if start_time and end_time and start_time > end_time:
            raise serializers.ValidationError("End time must be after the start time.")

        project = data.get('project')
        phase = data.get('phase')
        task = data.get('task')

        if phase and phase.project != project:
            raise serializers.ValidationError("The selected phase does not belong to the selected project.")

        if task and task.phase != phase:
            raise serializers.ValidationError("The selected task does not belong to the selected phase.")

        return data


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = ['id', 'name', 'description', 'is_paid', 'created_at', 'updated_at']


class AbsenceSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), required=False)
    leave_type = serializers.PrimaryKeyRelatedField(queryset=LeaveType.objects.all(), required=False)

    class Meta:
        model = Absence
        fields = ['absence_id', 'user', 'absence_date', 'start_time', 'end_time', 'absence_description', 'project', 'leave_type', 'is_deleted', 'created_at', 'updated_at']

    def validate(self, data):
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        if start_time and end_time and start_time > end_time:
            raise serializers.ValidationError("End time must be after the start time.")

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

        if phase and phase.project != project:
            raise serializers.ValidationError("The selected phase does not belong to the selected project.")

        if task and task.phase != phase:
            raise serializers.ValidationError("The selected task does not belong to the selected phase.")

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

        # Ensure the selected unit belongs to the selected entity
        if unit and entity:
            if unit.entity != entity:
                raise serializers.ValidationError({
                    'unit': 'The selected unit must belong to the selected entity.'
                })

        # Ensure the project belongs to the same entity
        if project and entity:
            if project.entity != entity:
                raise serializers.ValidationError({
                    'entity': 'The invoice must belong to the same entity as the project.'
                })

        # Ensure that the invoice date is valid if both dates are present
        invoice_date = data.get('invoice_date')
        if invoice_date and data.get('created_at') and invoice_date < data.get('created_at').date():
            raise serializers.ValidationError({
                'invoice_date': 'The invoice date cannot be before the creation date.'
            })

        return data
