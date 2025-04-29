from django.db import models
from .base import SoftDeleteModel
from .organisation_chart import OrganisationChart
from .entity import Entity

class OrganisationChartPositionAssignment(SoftDeleteModel):
    """
    Model representing position assignments within organizational charts
    Maps to tija_org_chart_position_assignments table
    """
    ENUM_CHOICES = [
        ('Y', 'Yes'),
        ('N', 'No')
    ]

    # Primary key
    positionAssignmentID = models.AutoField(primary_key=True)
    
    # Timestamp fields
    DateAdded = models.DateTimeField(auto_now_add=True)
    LastUpdate = models.DateTimeField(auto_now=True)
    
    # Foreign key relationships
    orgDataID = models.IntegerField()  # Reference to org data
    orgChartID = models.ForeignKey(
        OrganisationChart,
        on_delete=models.CASCADE,
        db_column='orgChartID',
        related_name='position_assignments'
    )
    entityID = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        db_column='entityID',
        related_name='position_assignments'
    )
    
    # Position details
    positionID = models.IntegerField()
    positionTypeID = models.IntegerField(null=True, blank=True)
    positionTitle = models.CharField(max_length=255)
    positionDescription = models.TextField(null=True, blank=True)
    positionParentID = models.IntegerField()
    positionOrder = models.IntegerField(null=True, blank=True)
    positionLevel = models.CharField(max_length=120, null=True, blank=True)
    positionCode = models.CharField(max_length=120, null=True, blank=True)
    
    # Tracking fields
    LastUpdatedByID = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='updated_position_assignments',
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
        db_table = 'tija_org_chart_position_assignments'
        verbose_name = 'Position Assignment'
        verbose_name_plural = 'Position Assignments'
        ordering = ['positionOrder', 'positionLevel', 'positionTitle']

    def __str__(self):
        """String representation of the position assignment"""
        return f"{self.positionTitle} - {self.orgChartID.orgChartName}"

    @property
    def status(self):
        """Return the current status of the position assignment"""
        if self.Suspended == 'Y':
            return 'Suspended'
        elif self.Lapsed == 'Y':
            return 'Lapsed'
        return 'Active'

    def get_subordinates(self):
        """Get all positions that report to this position"""
        return OrganisationChartPositionAssignment.objects.filter(
            orgChartID=self.orgChartID,
            positionParentID=self.positionID
        )

    def get_superior(self):
        """Get the position this position reports to"""
        try:
            return OrganisationChartPositionAssignment.objects.get(
                orgChartID=self.orgChartID,
                positionID=self.positionParentID
            )
        except OrganisationChartPositionAssignment.DoesNotExist:
            return None

    def get_hierarchy_level(self):
        """Calculate the hierarchical level of this position"""
        level = 1
        current = self
        while current.positionParentID != 0:  # Assuming 0 or similar for top level
            try:
                current = current.get_superior()
                if current:
                    level += 1
                else:
                    break
            except:
                break
        return level

    def suspend(self):
        """Suspend the position assignment"""
        self.Suspended = 'Y'
        self.save()

    def unsuspend(self):
        """Unsuspend the position assignment"""
        self.Suspended = 'N'
        self.save()

    def lapse(self):
        """Mark the position assignment as lapsed"""
        self.Lapsed = 'Y'
        self.save()

    def unlapse(self):
        """Remove lapsed status from the position assignment"""
        self.Lapsed = 'N'
        self.save()

    def save(self, *args, **kwargs):
        """Override save to update position level if not set"""
        if not self.positionLevel:
            self.positionLevel = f"Level {self.get_hierarchy_level()}"
        super().save(*args, **kwargs)

    @property
    def has_subordinates(self):
        """Check if position has any subordinates"""
        return self.get_subordinates().exists()

    @property
    def subordinates_count(self):
        """Get count of direct subordinates"""
        return self.get_subordinates().count()