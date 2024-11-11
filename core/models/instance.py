
from django.db import models
from .base import SoftDeleteModel

# Define an Instance model that represents a company instance with industry info
class Instance(SoftDeleteModel):
    INDUSTRY_CHOICES = []  # Placeholder for industry choices

    name = models.CharField(max_length=30)  # Instance name
    code = models.CharField(max_length=20)  # Short code for instance
    industry = models.CharField(max_length=30)  # Industry type

    def __str__(self):
        return self.name  # String representation of the instance
