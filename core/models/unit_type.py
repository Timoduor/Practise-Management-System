from django.db import models
from .base import SoftDeleteModel

class UnitType(SoftDeleteModel):
    name = models.CharField(max_length=40)
    description = models.TextField()