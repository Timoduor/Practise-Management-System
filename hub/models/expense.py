from django.db import models
from core.models.base import SoftDeleteModel
from core.models.user import User
from .project import Project
from .project_phase import ProjectPhase
from .task import Task


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

