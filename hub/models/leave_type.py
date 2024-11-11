from django.db import models
from core.models import SoftDeleteModel

class LeaveType(SoftDeleteModel):
    name = models.CharField(max_length=100, unique=True)  
    description = models.TextField(null=True, blank=True)  
    is_paid = models.BooleanField(default=False)  

    def __str__(self):
        return self.name