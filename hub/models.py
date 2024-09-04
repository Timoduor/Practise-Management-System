from django.db import models
from core.models import SoftDeleteModel, Entity, Unit, User

class Customer(SoftDeleteModel):
    customer_id = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField(unique=True)
    customer_phone = models.CharField(max_length=15, blank=True, null=True)
    customer_address = models.TextField(blank=True, null=True)

    entity = models.ForeignKey(Entity, on_delete=models.SET_NULL, blank=True, null=True)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.customer_name


class Project(SoftDeleteModel):
    project_id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=100)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="projects")
    project_description = models.TextField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    entity = models.ForeignKey(Entity, on_delete=models.SET_NULL, blank=True, null=True)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.project_name


class Task(SoftDeleteModel):
    task_id = models.AutoField(primary_key=True)
    task_name = models.CharField(max_length=100)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tasks")
    action_type = models.CharField(max_length=100)
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    task_description = models.TextField(null=True, blank=True)
    task_status = models.CharField(max_length=50)  # e.g., 'Pending', 'In Progress', 'Completed'

    entity = models.ForeignKey(Entity, on_delete=models.SET_NULL, null=True, blank=True)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.task_name
    

class Contact(SoftDeleteModel):
    contact_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="contacts")
    contact_name = models.CharField(max_length=100)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=15, blank=True, null=True)
    contact_address = models.TextField(blank=True, null=True)
    role = models.CharField(max_length=50, blank=True, null=True)  # e.g., 'Manager', 'Assistant'

    def __str__(self):
        return f"{self.contact_name} - {self.role} ({self.customer})"


class Sales(SoftDeleteModel):
    sales_id = models.AutoField(primary_key=True)
    sales_name = models.CharField(max_length=100)  
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    sales_description = models.TextField(null=True, blank=True)
    project_value = models.DecimalField(max_digits=10, decimal_places=2)  
    expected_order_date = models.DateField()

    SALES_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]

    sales_status = models.CharField(max_length=10, choices=SALES_STATUS_CHOICES, default='PENDING')
    project_manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="sales_manager")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="sales_creator")
    entity = models.ForeignKey(Entity, on_delete=models.SET_NULL, null=True, blank=True)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Sales {self.sales_id}: {self.sales_name}"  


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