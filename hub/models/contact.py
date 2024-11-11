from django.db import models
from core.models import SoftDeleteModel
from .customer import Customer


class Contact(SoftDeleteModel):
    contact_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="contacts")
    contact_name = models.CharField(max_length=100)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    contact_address = models.TextField(blank=True, null=True)
    contact_role = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.contact_name} - {self.role} ({self.customer})"

