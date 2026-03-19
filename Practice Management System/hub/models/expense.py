from django.db import models
from django.core.exceptions import ValidationError  # type: ignore
from core.models.base import SoftDeleteModel
from core.models.user import User
from .project import Project
from .project_phase import ProjectPhase
from .task import Task
from .customer import Customer
from .sales import Sales
from .sales_task import SalesTask


class Expense(SoftDeleteModel):  
    expense_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    phase = models.ForeignKey(ProjectPhase, on_delete=models.SET_NULL, null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    sale = models.ForeignKey(Sales, on_delete=models.SET_NULL, null=True, blank=True)
    sales_task = models.ForeignKey(SalesTask, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    duration = models.DurationField(null=True, blank=True, help_text="Duration in hours")
    value = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True, blank=True)
    supporting_document = models.FileField(upload_to='expenses/', null=True, blank=True)  # ✅ Added field

    def __str__(self):
        return f"Expense {self.expense_id} - {self.value} for {self.duration} hours"

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
