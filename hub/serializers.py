from datetime import datetime
from rest_framework import serializers
from core.models import User, Employee
from .models import Customer, Contact, Sales, Project, Task, Invoice, ProjectPhase, WorkEntries, Absence, Expense, LeaveType
from core.serializers import EmployeeSerializer

class ContactSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())

    class Meta:
        model = Contact
        fields = ['contact_id', 'contact_name', 'contact_email', 'contact_phone', 'contact_address', 'contact_role', 'customer', 'is_deleted', 'created_at', 'updated_at']


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


# class ProjectSerializer(serializers.ModelSerializer):
#     customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
#     members = EmployeeSerializer(many=True, read_only=True)
#     member_ids = serializers.PrimaryKeyRelatedField(
#         many=True, write_only=True, queryset=Employee.objects.all(), source='members'
#     )

#     class Meta:
#         model = Project
#         fields = ['project_id', 'project_name', 'customer', 'project_description', 'start_date', 'end_date', 'entity', 'unit', 'is_deleted', 'created_at', 'updated_at', 'members', 'member_ids']

#     def validate(self, data):
#         start_date = data.get('start_date')
#         end_date = data.get('end_date')
        
        
#         # Get the project instance from the context (if updating)
#         project_instance = self.instance
#         # Get the instance of the project (from project or request data)
#         project_instance = project_instance.entity.instance if project_instance else data['entity'].instance

#         # Ensure employees are from the same instance as the project
#         employees = data.get('members')
#         for employee in employees:
#             if employee.instance != project_instance:
#                 raise serializers.ValidationError(
#                     f"Employee {employee.user} does not belong to the same instance as the project."
#                 )


#         if start_date and end_date and start_date > end_date:
#             raise serializers.ValidationError("End date must be after the start date.")

#         entity = data.get('entity')
#         unit = data.get('unit')

#         if unit and entity:
#             if unit.entity != entity:
#                 raise serializers.ValidationError({
#                     'unit': 'The selected unit must belong to the selected entity.'
#                 })

#         return data

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


class ProjectPhaseSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    tasks = TaskSerializer(many=True, read_only= True)

    class Meta:
        model = ProjectPhase
        fields = ['phase_id', 'phase_name', 'project', 'phase_description', 'start_date', 'end_date', 'is_deleted', 'created_at', 'updated_at', 'tasks']

    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("End date must be after the start date.")

        return data


class ProjectSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    members = EmployeeSerializer(many=True, read_only=True)
    member_ids = serializers.PrimaryKeyRelatedField(
        many=True,  queryset=Employee.objects.all(), source='members'
    )
    phases = ProjectPhaseSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            'project_id', 'project_name', 'customer', 'project_description', 
            'start_date', 'end_date', 'entity', 'unit', 'is_deleted', 
            'created_at', 'updated_at','members', 'member_ids', 'phases'
        ]

    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        # Get the project instance (for update operations) or entity instance (for create operations)
        project_instance = self.instance
        project_instance = project_instance.entity.instance if project_instance else data['entity'].instance

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


class CustomerSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(many=True, read_only=True)
    
    sales = SalesSerializer(many=True, read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)

    class Meta:
        model = Customer
        fields = ['customer_id', 'customer_name', 'customer_email', 'customer_phone', 'customer_address', 'entity', 'unit', 'is_deleted', 'created_at', 'updated_at', 'contacts', 'sales', 'projects']

    def validate(self, data):
        entity = data.get('entity')
        unit = data.get('unit')

        if unit and entity:
            if unit.entity != entity:
                raise serializers.ValidationError({
                    'unit': 'The selected unit must belong to the selected entity.'
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
    
    def create(self, validated_data):
        # Calculate the duration and save it in the database
        start_time = validated_data.get('start_time')
        end_time = validated_data.get('end_time')
        
        today = datetime.today().date()  # Common date for both times

        # Combine date and time into datetime objects
        start_datetime = datetime.combine(today, start_time)
        end_datetime = datetime.combine(today, end_time)

        # Calculate the difference (this will be a timedelta object)
        validated_data["duration"] = end_datetime - start_datetime

        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Calculate the duration when updating as well
        start_time = validated_data.get('start_time', instance.start_time)
        end_time = validated_data.get('end_time', instance.end_time)
        today = datetime.today().date()  # Common date for both times

        # Combine date and time into datetime objects
        start_datetime = datetime.combine(today, start_time)
        end_datetime = datetime.combine(today, end_time)

        # Calculate the difference (this will be a timedelta object)
        instance.duration = end_datetime - start_datetime
        return super().update(instance, validated_data)


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = ['id', 'name', 'description', 'is_paid', 'created_at', 'updated_at']


class AbsenceSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), required=False)
    leave_type = serializers.PrimaryKeyRelatedField(queryset=LeaveType.objects.all(), required=False)

    class Meta:
        model = Absence
        fields = ['absence_id', 'user', 'absence_date', 'start_time', 'end_time','duration' ,'absence_description', 'project', 'leave_type', 'is_deleted', 'created_at', 'updated_at']

    def validate(self, data):
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        if start_time and end_time and start_time > end_time:
            raise serializers.ValidationError("End time must be after the start time.")

        return data

    def create(self, validated_data):
        # Calculate the duration and save it in the database
        start_time = validated_data.get('start_time')
        end_time = validated_data.get('end_time')

        
        today = datetime.today().date()  # Common date for both times

        # Combine date and time into datetime objects
        start_datetime = datetime.combine(today, start_time)
        end_datetime = datetime.combine(today, end_time)

        # Calculate the difference (this will be a timedelta object)
        validated_data["duration"] = end_datetime - start_datetime
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Calculate the duration when updating as well
        start_time = validated_data.get('start_time', instance.start_time)
        end_time = validated_data.get('end_time', instance.end_time)
        today = datetime.today().date()  # Common date for both times

        # Combine date and time into datetime objects
        start_datetime = datetime.combine(today, start_time)
        end_datetime = datetime.combine(today, end_time)

        # Calculate the difference (this will be a timedelta object)
        instance.duration = end_datetime - start_datetime
        return super().update(instance, validated_data)

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
