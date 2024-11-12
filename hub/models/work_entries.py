from django.db import models
from datetime import datetime
from core.models.base import SoftDeleteModel
from core.models.user import User
from .project import Project
from .project_phase import ProjectPhase
from .task import Task
from .task_type import TaskType


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
    task_type = models.ForeignKey(TaskType, on_delete=models.SET_NULL, null=True, blank=True, related_name="work_entries")

    def __str__(self):
        return f"Work entry on {self.project} - {self.phase} - {self.task}"

    def save(self, *args, **kwargs):
        if self.start_time and self.end_time:
            today = datetime.today().date()  # Common date for both times
            start_datetime = datetime.combine(today, self.start_time)
            end_datetime = datetime.combine(today, self.end_time)
            self.duration = end_datetime - start_datetime

        super().save(*args, **kwargs)
