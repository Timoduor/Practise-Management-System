from django.db import models
from .base import SoftDeleteModel

class UnitType(SoftDeleteModel):
    name = models.CharField(max_length=40, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name  # <-- Add this