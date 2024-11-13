from django.db import models
from datetime import datetime
from django.core.exceptions import ValidationError
from core.models.base import SoftDeleteModel
from core.models.user import User
from hub.models.customer import Customer
from hub.models.project import Project
from hub.models.project_phase import ProjectPhase
from hub.models.task import Task
from hub.models.task_type import TaskType
from hub.models.sales import Sales
from hub.models.sales_task import SalesTask


class WorkEntries(SoftDeleteModel):
    work_entries_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration = models.DurationField(editable=False, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    phase = models.ForeignKey(ProjectPhase, on_delete=models.SET_NULL, null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    task_type = models.ForeignKey(TaskType, on_delete=models.SET_NULL, null=True, blank=True, related_name="work_entries")
    sale = models.ForeignKey(Sales, on_delete=models.SET_NULL, null=True, blank=True)
    sales_task = models.ForeignKey(SalesTask, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Work entry on {self.date} - {self.start_time} - {self.end_time}"

    def clean(self):
        """
        Validate that only valid combinations of relationships are set.
        """
        if self.task and not self.project:
            raise ValidationError("A Task must be associated with a Project.")

        if not any([self.project, self.customer]):
            raise ValidationError("A WorkEntry must be related to at least a Project or Customer.")

    def save(self, *args, **kwargs):
        if self.start_time and self.end_time:
            today = datetime.today().date()
            start_datetime = datetime.combine(today, self.start_time)
            end_datetime = datetime.combine(today, self.end_time)
            self.duration = end_datetime - start_datetime
        super().save(*args, **kwargs)
