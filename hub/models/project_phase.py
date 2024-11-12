from django.db import models
from core.models.base import SoftDeleteModel
from core.models.employee import Employee
from .project import Project


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

