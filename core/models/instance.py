from django.db import models
from .base import SoftDeleteModel
from .industry_sector import IndustrySector  # Import the IndustrySector model

# Define an Instance model that represents a company instance with industry info
class Instance(SoftDeleteModel):
    INDUSTRY_CHOICES = [
        ('AGRI', 'Agriculture & Farming'),
        ('AUTO', 'Automotive'),
        ('BANK', 'Banking & Financial Services'),
        ('BIOTECH', 'Biotechnology'),
        ('CHEM', 'Chemicals & Materials'),
        ('COMM', 'Communications & Media'),
        ('CONS', 'Construction & Engineering'),
        ('CONS_GOODS', 'Consumer Goods'),
        ('CONS_SERV', 'Consumer Services'),
        ('EDU', 'Education'),
        ('ENERGY', 'Energy & Utilities'),
        ('ENTERTAIN', 'Entertainment & Media'),
        ('FASHION', 'Fashion & Apparel'),
        ('FOOD_BEV', 'Food & Beverage'),
        ('HEALTH', 'Healthcare'),
        ('HOSPITAL', 'Hospitality & Tourism'),
        ('INSUR', 'Insurance'),
        ('IT', 'Information Technology'),
        ('LEGAL', 'Legal Services'),
        ('LOGIST', 'Logistics & Transportation'),
        ('MANUF', 'Manufacturing'),
        ('MINING', 'Mining & Metals'),
        ('NGO', 'Non-Profit & NGO'),
        ('PHARMA', 'Pharmaceuticals'),
        ('PROP', 'Property & Real Estate'),
        ('RETAIL', 'Retail'),
        ('TECH', 'Technology'),
        ('TELCO', 'Telecommunications'),
        ('TRADE', 'Trading & Commerce'),
        ('OTHER', 'Other')
    ]  # Comprehensive list of industry choices

    instanceID = models.AutoField(primary_key=True)  # Primary key
    DateAdded = models.DateTimeField(auto_now_add=True)  # Automatically set when created
    instanceName = models.CharField(max_length=256)  # Instance name
    industrySector = models.ForeignKey(
        IndustrySector,
        on_delete=models.CASCADE,
        related_name="instances"
    )  # ForeignKey to IndustrySector for dropdown
    Lapsed = models.BooleanField(default=False)  # Enum-like field for lapsed status
    Suspended = models.BooleanField(default=False)  # Enum-like field for suspended status

    def __str__(self):
        return self.instanceName  # String representation of the instance