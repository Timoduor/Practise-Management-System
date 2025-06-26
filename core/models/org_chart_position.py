from django.db import models
from django.utils.timezone import now

class OrgChartPositionAssignment(models.Model):
    positionAssignmentID = models.AutoField(primary_key=True)
    DateAdded = models.DateTimeField(default=now)
    orgDataID = models.ForeignKey(
        'OrganisationData',
        on_delete=models.CASCADE,
        related_name='position_assignments'
    )
    orgChartID = models.ForeignKey(
        'OrgChart', 
        on_delete=models.CASCADE, 
        related_name='position_assignments'
    )
    instanceID = models.ForeignKey(
        'Instance', 
        on_delete=models.CASCADE, 
        related_name='position_assignments'
    )
    entityID = models.ForeignKey(
        'Entity',
        on_delete=models.CASCADE,
        related_name='position_assignments',
    )
    positionID = models.ForeignKey(
        'JobPosition',
        on_delete=models.CASCADE,
        related_name='position_assignments'
    )

    positionAssignmentParentID = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_assignments'
    )
    positionCode = models.CharField(max_length=50, unique=True)
    LastUpdate = models.DateTimeField(auto_now=True)
    LastUpdatedByID = models.IntegerField()
    Lapsed = models.CharField(max_length=1, choices=[('Y', 'Yes'), ('N', 'No')], default='N')
    Suspended = models.CharField(max_length=1, choices=[('Y', 'Yes'), ('N', 'No')], default='N')

    def __str__(self):
        return f"Position Assignment {self.positionAssignmentID} - {self.positionCode}"