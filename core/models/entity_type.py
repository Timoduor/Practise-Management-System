from django.db import models
from .base import SoftDeleteModel

class EntityType(SoftDeleteModel):
    """
    Model representing entity types
    """
    entityTypeID = models.AutoField(primary_key=True)  # Primary key
    DateAdded = models.DateTimeField(auto_now_add=True)  # Automatically set when created
    entityTypeTitle = models.CharField(max_length=256, unique=True)  # Title of the entity type
    entityTypeDescription = models.TextField()  # Description of the entity type
    LastUpdate = models.DateTimeField(auto_now=True)  # Automatically updated on save
    Lapsed = models.BooleanField(default=False)  # Enum-like field for lapsed status
    Suspended = models.BooleanField(default=False)  # Enum-like field for suspended status

    def __str__(self):
        return self.entityTypeTitle  # String representation of the entity type