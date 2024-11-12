from django.db import models
from django.core.exceptions import ValidationError  
from datetime import datetime, timedelta
from core.models.base import SoftDeleteModel
from core.models.user import User
from .project import Project
from .leave_type import LeaveType
from .sales import Sales


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
            today = datetime.combine(self.absence_date, self.start_time)
            end_datetime = datetime.combine(self.absence_date, self.end_time)

            # If end time is earlier than start time, assume the end time is on the next day
            if end_datetime < today:
                end_datetime += timedelta(days=1)

            self.duration = end_datetime - today
        super().save(*args, **kwargs)

