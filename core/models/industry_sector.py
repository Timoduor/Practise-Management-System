from django.db import models
from django.conf import settings

class IndustrySector(models.Model):
    SUSPENDED_CHOICES = [
        ('Y', 'Yes'),
        ('N', 'No'),
    ]

    industrySectorID = models.AutoField(primary_key=True)
    DateAdded = models.DateTimeField(auto_now_add=True)
    industryTitle = models.CharField(max_length=255)
    industryCategory = models.CharField(max_length=255)
    LastUpdatedByID = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column='LastUpdatedByID'
    )
    Suspended = models.CharField(max_length=1, choices=SUSPENDED_CHOICES, default='N')

    def __str__(self):
        return self.industryTitle