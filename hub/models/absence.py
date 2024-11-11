from django.db import models
from datetime import datetime
from core.models import SoftDeleteModel, User
from .project import Project
from .leave_type import LeaveType


class Absence(SoftDeleteModel):  
    absence_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    absence_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration = models.DurationField(editable=False, null=True, blank=True)
    absence_description = models.TextField(null=True, blank=True)

    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.leave_type} on {self.absence_date}"
    
    def save(self, *args, **kwargs):
        if self.start_time and self.end_time:

            today = datetime.today().date()  # Common date for both times
            # Combine date and time into datetime objects
            start_datetime = datetime.combine(today, self.start_time)
            
            end_datetime = datetime.combine(today, self.end_time)

            # Calculate the difference (this will be a timedelta object)
            self.duration = end_datetime - start_datetime

        super().save(*args, **kwargs)

