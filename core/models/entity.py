from django.db import models
from .base import SoftDeleteModel

class Entity(SoftDeleteModel):
    """
    Model representing entities within instances, like companies.
    """
    entityID = models.AutoField(primary_key=True)  # Primary key
    DateAdded = models.DateTimeField(auto_now_add=True)  # Automatically set when created
    entityName = models.CharField(max_length=256)  # Entity name
    entityDescription = models.TextField()  # Description of the entity
    entityTypeID = models.ForeignKey("core.EntityType", on_delete=models.SET_NULL, null=True, related_name="entities")  # FK to tija_entity_types
    instanceID = models.ForeignKey("core.Instance", on_delete=models.SET_NULL, null=True, blank=True, related_name="entities")  # FK to tija_instances
    orgDataID = models.ForeignKey("core.OrganisationData", on_delete=models.SET_NULL, null=True, blank=True, related_name="entities")  # FK to tija_organisation_data
    entityParentID = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="child_entities")  # FK to tija_entities
    industrySectorID = models.ForeignKey("core.IndustrySector", on_delete=models.SET_NULL, null=True, blank=True, related_name="entities")  # FK to industry_sectors
    registrationNumber = models.CharField(max_length=50, blank=True, null=True)  # Registration number
    entityPIN = models.CharField(max_length=50, blank=True, null=True)  # Entity PIN
    entityCity = models.CharField(max_length=100, blank=True, null=True)  # Entity city
    entityCountry = models.CharField(max_length=100, blank=True, null=True)  # Entity country
    entityPhoneNumber = models.CharField(max_length=20, blank=True, null=True)  # Entity phone number
    entityEmail = models.EmailField(blank=True, null=True)  # Entity email
    LastUpdate = models.DateTimeField(auto_now=True)  # Automatically updated on save
    LastUpdateByID = models.ForeignKey("core.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="updated_entities")  # FK to tija_users
    Lapsed = models.BooleanField(default=False)  # Enum-like field for lapsed status
    Suspended = models.BooleanField(default=False)  # Enum-like field for suspended status

    def __str__(self):
        return f"{self.entityName} ({self.instanceID})"  # String representations