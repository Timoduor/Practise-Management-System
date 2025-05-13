from django.db import models
from .base import SoftDeleteModel
from .organisation_chart import OrganisationChart
from django.core.exceptions import ValidationError

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
    orgChartID = models.ForeignKey(
        OrganisationChart,
        on_delete=models.CASCADE,
        db_column='orgChartID',
        related_name='position_assignments'
    )
    
    # Position details
    positionID = models.IntegerField()
    # positionTypeID = models.IntegerField(null=True, blank=True) - not necessary as of now
    positionTitle = models.CharField(max_length=255)
    positionDescription = models.TextField(null=True, blank=True)
    positionParentID = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,  # Allow blank for top-level positions
        related_name='subordinates',
        db_column='positionParentID'
    )
    positionOrder = models.IntegerField(null=True, blank=True) # automatically generated - look @ save() method
    positionLevel = models.CharField(max_length=120, null=True, blank=True) # automatically generated - look @ save() method
    positionCode = models.CharField(max_length=120, null=True, blank=True) # automatically generated - look @ save() method
    
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
        # Use the related_name from the foreign key
        return self.subordinates.all()

    def get_superior(self):
        """Get the position this position reports to"""
        # Simply return the foreign key value - no query needed
        return self.positionParentID

    def get_hierarchy_level(self):
        """Calculate the hierarchical level of this position"""
        level = 1
        current = self
        # Changed comparison from integer to None
        while current.positionParentID is not None:
            current = current.positionParentID  # Direct reference, no query needed
            level += 1
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
        """Override save to update position level, auto-generate position code, and set positionOrder"""
        # Run validation
        self.full_clean()
        
        # Set position level if not provided
        if not self.positionLevel:
            self.positionLevel = f"Level {self.get_hierarchy_level()}"
        
        # Auto-assign positionOrder if not provided (max+1 of siblings)
        if self.positionOrder is None:
            # Find siblings (positions with same parent in same org chart)
            siblings_filter = {
                'orgChartID': self.orgChartID,
                'positionParentID': self.positionParentID
            }
            
            # Get max order of siblings
            max_order = OrganisationChartPositionAssignment.objects.filter(
                **siblings_filter
            ).aggregate(models.Max('positionOrder'))['positionOrder__max'] or 0
            
            # Assign as max+1
            self.positionOrder = max_order + 1
        
        # Perform initial save if this is a new object
        is_new = self.pk is None
        if is_new:
            super().save(*args, **kwargs)
        
        # Now generate position code with available IDs
        org_prefix = str(self.orgChartID.pk)[:3].upper()
        entity_prefix = str(self.orgChartID.entityID.pk)[:3].upper()
        level = self.get_hierarchy_level()
        position_id = self.pk
        self.positionCode = f"{org_prefix}-{entity_prefix}-L{level}-P{position_id}"
        
        # Save again if this is a new object or always save if it's existing
        if is_new:
            # Use update to avoid recursive save
            type(self).objects.filter(pk=self.pk).update(positionCode=self.positionCode)
        else:
            super().save(*args, **kwargs)

    @property
    def has_subordinates(self):
        """Check if position has any subordinates"""
        return self.get_subordinates().exists()

    @property
    def subordinates_count(self):
        """Get count of direct subordinates"""
        return self.get_subordinates().count()

    def clean(self):
        """Validate that parent position is in the same org chart"""
        if self.positionParentID and self.positionParentID.orgChartID != self.orgChartID:
            raise ValidationError({
                'positionParentID': 'Parent position must be in the same organization chart.'
            })
        
        # Check for circular references
        if self._check_circular_reference():
            raise ValidationError({
                'positionParentID': 'Circular reference detected in position hierarchy.'
            })
        
    def _check_circular_reference(self):
        """Check if there's a circular reference in the position hierarchy"""
        if not self.positionParentID:
            return False
            
        # Get all ancestors to check for circularity
        visited = set()
        current = self.positionParentID
        while current:
            if current.id in visited:
                return True  # Circular reference found
            visited.add(current.id)
            current = current.positionParentID
        return False