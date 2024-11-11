from django.db import models
from .base import SoftDeleteModel

# Define an Entity model to represent entities within instances, like companies
class Entity(SoftDeleteModel):
    ENTITY_TYPES = [
        ("SEC", "Single Entity Company"),
        ("HC", "Holding Company")
    ]

    name = models.CharField(max_length=30)  # Entity name
    # entity_type = models.CharField(max_length=15, choices=ENTITY_TYPES, default="Single Entity Company")
    entity_type = models.ForeignKey("core.EntityType", on_delete=models.SET_NULL, null =True)
    description = models.TextField()  # Description of the entity
    instance = models.ForeignKey("core.Instance", on_delete=models.SET_NULL, blank=True, null=True, related_name="entities")  # Related instance
    parent_entity = models.ForeignKey("self", on_delete=models.SET_NULL, blank=True, null=True)  # Optional parent entity for hierarchy

    def __str__(self):
        return f"{self.instance} - {self.name}"  # String representation
