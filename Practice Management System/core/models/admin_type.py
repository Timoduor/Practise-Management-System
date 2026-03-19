from django.db import models
from .base import SoftDeleteModel

# Define AdminType model to categorize admin types
class AdminType(SoftDeleteModel):
    name = models.CharField(max_length=15, unique=True)  # Type name (e.g., "SUP")
    description = models.TextField()  # Description of the admin type

    def __str__(self) -> str:
        return self.name  # String representation of the admin type
