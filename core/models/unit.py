from django.db import models
from .base import SoftDeleteModel

# Define a Unit model representing smaller divisions within an entity (e.g., branches)
class Unit(SoftDeleteModel):
    UNIT_TYPES = [
        ("BR", "Branch"),
        ("DEP", "Department"),
        ("SEC", "Section"),
        ("TEA", "Team")
    ]

    name = models.CharField(max_length=15)  # Unit name
    address = models.TextField(null=True, blank=True)  # Optional unit address
    unit_type = models.CharField(max_length=3, choices=UNIT_TYPES, default="DEP")  # Unit type
    entity = models.ForeignKey("Entity", on_delete=models.SET_NULL, blank=True, null=True, related_name="units")  # Related entity

    def __str__(self):
        return f"{self.entity} - {self.name}"  # String representation
