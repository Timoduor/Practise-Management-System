from django.db import models
from .base import SoftDeleteModel
from .entity import Entity
from .organisation_data import OrganisationData

class OrganisationChart(SoftDeleteModel):
    """
    Model representing organizational charts linked to entities
    Maps to tija_org_charts table
    """
    ENUM_CHOICES = [
        ('Y', 'Yes'),
        ('N', 'No')
    ]

    # Primary key
    orgChartID = models.AutoField(primary_key=True)
    
    # Basic fields
    DateAdded = models.DateTimeField(auto_now_add=True)
    orgChartName = models.CharField(max_length=256)
    
    # Foreign key relationships
    orgDataID = models.OneToOneField(
        OrganisationData,
        on_delete=models.CASCADE,
        db_column='orgDataID',
        related_name='organisation_chart'
    )
    entityID = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        db_column='entityID'
    )
    
    # Tracking fields
    LastUpdate = models.DateTimeField(auto_now=True)
    LastUpdatedByID = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='updated_org_charts',
        db_column='LastUpdatedByID'
    )
    
    # Status fields
    Lapsed = models.CharField(
        max_length=1,
        choices=ENUM_CHOICES,
        default='N'
    )
    Suspended = models.CharField(
        max_length=1,
        choices=ENUM_CHOICES,
        default='N'
    )

    class Meta:
        db_table = 'tija_org_charts'
        verbose_name = 'Organization Chart'
        verbose_name_plural = 'Organization Charts'
        ordering = ['-DateAdded']

    def __str__(self):
        """String representation of the organization chart"""
        return f"{self.orgChartName} - {self.entityID}"

    @property
    def status(self):
        """Return the current status of the organization chart"""
        if self.Suspended == 'Y':
            return 'Suspended'
        elif self.Lapsed == 'Y':
            return 'Lapsed'
        return 'Active'

    def suspend(self):
        """Suspend the organization chart"""
        self.Suspended = 'Y'
        self.save()

    def unsuspend(self):
        """Unsuspend the organization chart"""
        self.Suspended = 'N'
        self.save()

    def lapse(self):
        """Mark the organization chart as lapsed"""
        self.Lapsed = 'Y'
        self.save()

    def unlapse(self):
        """Remove lapsed status from the organization chart"""
        self.Lapsed = 'N'
        self.save()