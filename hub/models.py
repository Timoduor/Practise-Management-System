from datetime import datetime
from django.db import models
from core.models import SoftDeleteModel, Entity, Unit, User, Employee

class Customer(SoftDeleteModel):
    customer_id = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField(unique=True)
    customer_phone = models.CharField(max_length=20, blank=True, null=True)
    customer_address = models.TextField(blank=True, null=True)

    entity = models.ForeignKey(Entity, on_delete=models.SET_NULL, blank=True, null=True)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.customer_name

class Sales(SoftDeleteModel):
    sales_id = models.AutoField(primary_key=True)
    sales_name = models.CharField(max_length=100)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name="sales")
    sales_description = models.TextField(null=True, blank=True)
    project_value = models.DecimalField(max_digits=10, decimal_places=2)
    expected_order_date = models.DateField()

    SALES_STATUS_CHOICES = [
        ('LEAD', 'Lead'),
        ('OPPORTUNITY', 'Opportunity'),
        ('PROPOSAL', 'Proposal'),
        ('CLOSED_REJECTED', 'Rejected'),
        ('CLOSED_ACCPETED', 'Accepted')
    ]
    
    sales_status = models.CharField(max_length=20, choices=SALES_STATUS_CHOICES, default='PENDING')
    project_manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name="sales_manager")
    members = models.ManyToManyField(Employee, related_name="sales_members")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="sales_creator")
    entity = models.ForeignKey(Entity, on_delete=models.SET_NULL, null=True, blank=True)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Sales {self.sales_id}: {self.sales_name}"  





class Project(SoftDeleteModel):
    project_id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=100)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="projects")
    project_description = models.TextField(blank=True, null=True)

    project_value = models.DecimalField(max_digits=10, decimal_places=2)

    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    project_manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name="project_manager")

    members = models.ManyToManyField(Employee, related_name="project_members")

    sale = models.ForeignKey(Sales, on_delete=models.CASCADE, null=True, blank=True, related_name="related_project")

    entity = models.ForeignKey(Entity, on_delete=models.SET_NULL, blank=True, null=True)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.project_name


class ProjectPhase(SoftDeleteModel):  
    phase_id = models.AutoField(primary_key=True)
    phase_name = models.CharField(max_length=100)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="phases")
    phase_description = models.TextField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Phase: {self.phase_name} of {self.project.project_name}"


class Task(SoftDeleteModel):  
    task_id = models.AutoField(primary_key=True)
    task_name = models.CharField(max_length=100)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    phase = models.ForeignKey(ProjectPhase, on_delete=models.CASCADE, related_name="tasks")
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tasks")
    task_description = models.TextField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    
    TASK_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed')
    ]
    task_status = models.CharField(max_length=50, choices=TASK_STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"{self.task_name} in {self.phase.phase_name}"


class WorkEntries(SoftDeleteModel):  
    work_entries_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration = models.DurationField(editable=False, null=True, blank=True)    
    description = models.TextField(null=True, blank=True)
    
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    phase = models.ForeignKey(ProjectPhase, on_delete=models.SET_NULL, null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    
    TASK_TYPE_CHOICES = [
        ('CONSULTING', 'Consulting'),
        ('INTERNAL_WORK', 'Internal Work'),
        ('TRANSACTIONAL', 'Transactional'),
        ('PROJECT_TASK', 'Project Task'),
        ('NORMAL_ACTIVITIES', 'Normal Activities'),
        ('OTHER', 'Other'),
    ]
    task_type = models.CharField(max_length=50, choices=TASK_TYPE_CHOICES)

    def __str__(self):
        return f"Work entry on {self.project} - {self.phase} - {self.task}"
    
    def save(self, *args, **kwargs):
        if self.start_time and self.end_time:

            today = datetime.today().date()  # Common date for both times
            # Combine date and time into datetime objects
            start_datetime = datetime.combine(today, self.start_time)
            
            end_datetime = datetime.combine(today, self.end_time)

            # Calculate the difference (this will be a timedelta object)
            self.duration = end_datetime - start_datetime

        super().save(*args, **kwargs)


class LeaveType(SoftDeleteModel):
    name = models.CharField(max_length=100, unique=True)  
    description = models.TextField(null=True, blank=True)  
    is_paid = models.BooleanField(default=False)  

    def __str__(self):
        return self.name


class Absence(SoftDeleteModel):  
    absence_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    absence_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration = models.DurationField(editable=False, null=True, blank=True)
    absence_description = models.TextField(null=True, blank=True)

    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.leave_type} on {self.absence_date}"
    
    def save(self, *args, **kwargs):
        if self.start_time and self.end_time:

            today = datetime.today().date()  # Common date for both times
            # Combine date and time into datetime objects
            start_datetime = datetime.combine(today, self.start_time)
            
            end_datetime = datetime.combine(today, self.end_time)

            # Calculate the difference (this will be a timedelta object)
            self.duration = end_datetime - start_datetime

        super().save(*args, **kwargs)


class Expense(SoftDeleteModel):  
    expense_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    phase = models.ForeignKey(ProjectPhase, on_delete=models.SET_NULL, null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    value = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Expense {self.expense_id} - {self.value} on {self.project}"


class Contact(SoftDeleteModel):
    contact_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="contacts")
    contact_name = models.CharField(max_length=100)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    contact_address = models.TextField(blank=True, null=True)
    contact_role = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.contact_name} - {self.role} ({self.customer})"



class Invoice(SoftDeleteModel):
    invoice_id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    invoice_amount = models.DecimalField(max_digits=10, decimal_places=2)
    invoice_date = models.DateField()
    paid_status = models.BooleanField(default=False)

    entity = models.ForeignKey(Entity, on_delete=models.SET_NULL, null=True, blank=True)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Invoice {self.invoice_id}: {self.invoice_amount}"
