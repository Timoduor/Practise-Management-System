from django.db import models
from core.models.base import SoftDeleteModel
from core.models.employee import Employee
from .project import Project
from .project_phase import ProjectPhase
from .task_status import TaskStatus
from .task_type import TaskType

class Task(SoftDeleteModel):
    task_id = models.AutoField(primary_key=True)
    task_name = models.CharField(max_length=100)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    phase = models.ForeignKey(ProjectPhase, on_delete=models.CASCADE, related_name="tasks")
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tasks")
    task_description = models.TextField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    task_status = models.ForeignKey(TaskStatus, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks")
    task_type = models.ForeignKey(TaskType, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks")
    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return f"{self.task_name} in {self.phase.phase_name}"
    
