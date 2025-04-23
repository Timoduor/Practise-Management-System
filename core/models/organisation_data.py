from django.db import models
from django.conf import settings

class OrganisationData(models.Model):
    COST_CENTER_CHOICES = [
        ('ENABLED', 'Enabled'),
        ('DISABLED', 'Disabled'),
    ]

    LAPSED_CHOICES = [
        ('YES', 'Yes'),
        ('NO', 'No'),
    ]

    SUSPENDED_CHOICES = [
        ('YES', 'Yes'),
        ('NO', 'No'),
    ]

    orgDataID = models.AutoField(primary_key=True)
    DateAdded = models.DateTimeField(auto_now_add=True)
    instanceID = models.ForeignKey('core.Instance', on_delete=models.CASCADE)
    orgLogo = models.CharField(max_length=255)
    orgName = models.CharField(max_length=255)
    industrySectorID = models.ForeignKey('core.IndustrySector', on_delete=models.CASCADE)
    numberOfEmployees = models.IntegerField()
    registrationNumber = models.CharField(max_length=255)
    orgPIN = models.CharField(max_length=255)
    costCenterEnabled = models.CharField(max_length=10, choices=COST_CENTER_CHOICES)
    orgAddress = models.CharField(max_length=255)
    orgPostalCode = models.CharField(max_length=20)
    orgCity = models.CharField(max_length=100)
    orgCountry = models.CharField(max_length=100)
    orgPhoneNumber1 = models.CharField(max_length=20)
    orgPhoneNumber2 = models.CharField(max_length=20, blank=True, null=True)
    orgEmail = models.EmailField()
    LastUpdate = models.DateTimeField(auto_now=True)
    LastUpdatedByID = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column='LastUpdatedByID'
    )
    Lapsed = models.CharField(max_length=10, choices=LAPSED_CHOICES)
    Suspended = models.CharField(max_length=10, choices=SUSPENDED_CHOICES)

    def __str__(self):
        return self.orgName