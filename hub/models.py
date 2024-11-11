from datetime import datetime
from django.db import models
from core.models import SoftDeleteModel, Entity, Unit, User, Employee
from django.core.exceptions import ValidationError

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
        ('CLOSED_ACCEPTED', 'Accepted')
    ]
    
    sales_status = models.CharField(max_length=20, choices=SALES_STATUS_CHOICES, default='PENDING')
    project_manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name="sales_manager")
    members = models.ManyToManyField(Employee,blank=True ,related_name="sales_members")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="sales_creator")
    
    entity = models.ForeignKey(Entity, on_delete=models.SET_NULL, null=True, blank=True)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['expected_order_date']

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

    members = models.ManyToManyField(Employee, blank=True,  related_name="project_members")

    sale = models.ForeignKey(Sales, on_delete=models.CASCADE, null=True, blank=True, related_name="related_project")

    entity = models.ForeignKey(Entity, on_delete=models.SET_NULL, blank=True, null=True)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        ordering = ['start_date']
    
    def __str__(self):
        return self.project_name


class ProjectPhase(SoftDeleteModel):  
    phase_id = models.AutoField(primary_key=True)
    phase_name = models.CharField(max_length=100)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="phases")
    phase_description = models.TextField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    members = models.ManyToManyField(Employee, blank=True,  related_name="phase_members")

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        return f"Phase: {self.phase_name} of {self.project.project_name}"


class Task(SoftDeleteModel):  
    task_id = models.AutoField(primary_key=True)
    task_name = models.CharField(max_length=100)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    phase = models.ForeignKey(ProjectPhase, on_delete=models.CASCADE, related_name="tasks")
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tasks")
    task_description = models.TextField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    
    TASK_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed')
    ]
    task_status = models.CharField(max_length=50, choices=TASK_STATUS_CHOICES, default='PENDING')
    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return f"{self.task_name} in {self.phase.phase_name}"


class SalesTask(SoftDeleteModel):  
    sales_task_id = models.AutoField(primary_key=True)
    task_name = models.CharField(max_length=100)
    sale = models.ForeignKey(Sales, on_delete=models.SET_NULL, null=True, blank=True, related_name="sales_tasks")

    TASK_TYPES = [
        ('CALL', 'Call'),
        ('MEETING', 'Meeting'),
        ('TO_DO', 'Todo')
    ]   


    task_type = models.CharField(max_length=50, choices=TASK_TYPES, default='TO_DO')
    
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_sales_tasks")
    task_description = models.TextField(null=True, blank=True)

    date = models.DateField(null=True, blank=True)
    
    TASK_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed')
    ]
    task_status = models.CharField(max_length=50, choices=TASK_STATUS_CHOICES, default='PENDING')

    class Meta:
        ordering = ['date']

    def __str__(self):
            return f"{self.task_name} in {self.sale.sales_name if self.sale else 'No Sale'}"



class WorkEntries(SoftDeleteModel):  
    work_entries_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration = models.DurationField(editable=False, null=True, blank=True)    
    description = models.TextField(null=True, blank=True)


    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)




    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)


    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    phase = models.ForeignKey(ProjectPhase, on_delete=models.SET_NULL, null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)    


    sale = models.ForeignKey(Sales, on_delete=models.SET_NULL, null=True, blank=True)
    sales_task = models.ForeignKey(SalesTask, on_delete=models.SET_NULL, null=True, blank=True)
    
    
    
    TASK_TYPE_CHOICES = [
        ('CONSULTING', 'Consulting'),
        ('INTERNAL_WORK', 'Internal Work'),
        ('TRANSACTIONAL', 'Transactional'),
        ('PROJECT_TASK', 'Project Task'),
        ('NORMAL_ACTIVITIES', 'Normal Activities'),
        ('OTHER', 'Other'),
    ]
    task_type = models.CharField(max_length=50, choices=TASK_TYPE_CHOICES, default="NORMAL_ACTIVITIES")

    def __str__(self):
        return f"Work entry on {self.project} - {self.phase} - {self.task}"
    
    def clean(self):
        """
        Validate that only valid combinations of relationships are set.
        """
        if (self.project or self.task) and (self.sale or self.sales_task):
            raise ValidationError("A WorkEntry can relate to either a Project/Task or Sale/SalesTask, but not both.")

        if self.task and not self.project:
            raise ValidationError("A Task must be associated with a Project.")

        if self.sales_task and not self.sale:
            raise ValidationError("A SalesTask must be associated with a Sale.")

        if not any([self.project, self.sale, self.customer]):
            raise ValidationError("A WorkEntry must be related to at least one of Project, Sale, or Customer.")
    
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
    sale = models.ForeignKey(Sales, on_delete=models.SET_NULL, null=True, blank=True)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.leave_type} on {self.absence_date}"

    def clean(self):
        if self.project and self.sale:
            raise ValidationError("An Absence can relate to either a Project or Sale, but not both.")
        
        if not any([self.project, self.sale]):
            raise ValidationError("An Absence must be related to either a Project or Sale.")

    def save(self, *args, **kwargs):
        if self.start_time and self.end_time:
            today = datetime.today().date()
            start_datetime = datetime.combine(today, self.start_time)
            end_datetime = datetime.combine(today, self.end_time)
            self.duration = end_datetime - start_datetime
        super().save(*args, **kwargs)


class Expense(SoftDeleteModel):  
    expense_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    phase = models.ForeignKey(ProjectPhase, on_delete=models.SET_NULL, null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)

    sale = models.ForeignKey(Sales, on_delete=models.SET_NULL ,null=True, blank=True)
    sales_task =models.ForeignKey(SalesTask, on_delete=models.SET_NULL ,null=True, blank=True)
    date = models.DateField()
    value = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Expense {self.expense_id} - {self.value} on {self.project}"
    
    def clean(self):
        """
        Validate that only valid combinations of relationships are set.
        """
        if (self.project or self.phase or self.task) and (self.sale or self.sales_task):
            raise ValidationError("An Expense can relate to either a Project/Task or Sale/SalesTask, but not both.")

        if self.task and not self.project:
            raise ValidationError("A Task must be associated with a Project.")

        if self.sales_task and not self.sale:
            raise ValidationError("A SalesTask must be associated with a Sale.")

        if not any([self.project, self.sale, self.customer]):
            raise ValidationError("An Expense must be related to at least one of Project, Sale, or Customer.")


class Contact(SoftDeleteModel):
    contact_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="contacts")
    contact_name = models.CharField(max_length=100)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    contact_address = models.TextField(blank=True, null=True)
    contact_role = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.contact_name} - {self.contact_role or 'No Role'} ({self.customer})"



class Invoice(SoftDeleteModel):
    invoice_id = models.AutoField(primary_key=True)
    project = models.ForeignKey('Project', on_delete=models.SET_NULL, null=True, blank=True)
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

    def clean(self):
        super().clean()
        if not self.customer:
            raise ValidationError("An Invoice must have a related Customer.")

