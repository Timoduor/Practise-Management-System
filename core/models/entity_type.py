from django.db import models
from .base import SoftDeleteModel

class EntityType(SoftDeleteModel):
    name = models.CharField(max_length=40, unique=True)
    description = models.TextField()
