from django.db import models
from core.models.base import SoftDeleteModel
from core.models.employee import Employee
from .sales import Sales
from .sales_task_status import SalesTaskStatus
from .sales_task_type import SalesTaskType


class SalesTask(SoftDeleteModel):
    sales_task_id = models.AutoField(primary_key=True)
    task_name = models.CharField(max_length=100)
    sale = models.ForeignKey(Sales, on_delete=models.SET_NULL, null=True, blank=True, related_name="sales_tasks")

    # Replace task_type with a ForeignKey to SalesTaskType
    task_type = models.ForeignKey(SalesTaskType, on_delete=models.SET_NULL, null=True, blank=True, related_name="sales_tasks")

    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_sales_tasks")
    task_description = models.TextField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)

    # Replace task_status with a ForeignKey to SalesTaskStatus
    task_status = models.ForeignKey(SalesTaskStatus, on_delete=models.SET_NULL, null=True, blank=True, related_name="sales_tasks")

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.task_name} in {self.sale.sales_name if self.sale else 'No Sale'}"
