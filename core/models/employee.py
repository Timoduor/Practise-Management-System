from django.db import models
from .base import SoftDeleteModel

#Define Employee model to link users to instances, entities, and units
class Employee(SoftDeleteModel):
    user = models.OneToOneField("User", on_delete=models.CASCADE, related_name="employee_user")  # Linked user account
    instance = models.ForeignKey("Instance", on_delete=models.CASCADE)  # Related instance
    entity = models.ForeignKey("Entity", on_delete=models.CASCADE, blank=True, null=True)  # Related entity
    unit = models.ForeignKey("Unit", on_delete=models.SET_NULL, blank=True, null=True)  # Optional unit
    
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"  # Or `self.user.username` or `self.user.email`