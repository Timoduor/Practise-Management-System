from django.db import models
from core.models import SoftDeleteModel, Entity, Unit, User, Employee
from .customer import Customer
from .sales_type import SalesType

class Sales(SoftDeleteModel):
    sales_id = models.AutoField(primary_key=True)
    sales_name = models.CharField(max_length=100)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name="sales")
    sales_description = models.TextField(null=True, blank=True)
    project_value = models.DecimalField(max_digits=10, decimal_places=2)
    expected_order_date = models.DateField()
    sales_status = models.ForeignKey(SalesType, on_delete=models.SET_NULL, null=True, blank=True, related_name="sales")
    project_manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name="sales_manager")
    members = models.ManyToManyField(Employee, blank=True, related_name="sales_members")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="sales_creator")
    entity = models.ForeignKey(Entity, on_delete=models.SET_NULL, null=True, blank=True)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['expected_order_date']

    def __str__(self):
        return f"Sales {self.sales_id}: {self.sales_name}"
