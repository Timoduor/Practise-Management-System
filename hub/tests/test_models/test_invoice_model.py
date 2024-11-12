from django.test import TestCase
from django.core.exceptions import ValidationError
from hub.models.invoice import Invoice
from hub.models.customer import Customer
from hub.models.project import Project
from core.models.entity import Entity
from core.models.unit import Unit
from datetime import date

class InvoiceModelTest(TestCase):
    def setUp(self):
        self.entity = Entity.objects.create(name="Test Entity", entity_type="SEC", description="Entity Description")
        self.unit = Unit.objects.create(name="Test Unit", entity=self.entity, unit_type="BR")
        self.customer = Customer.objects.create(
            customer_name="Test Customer",
            customer_email="customer@example.com",
            entity=self.entity,
            unit=self.unit
        )
        self.project = Project.objects.create(
            project_name="Test Project",
            customer=self.customer,
            project_value=50000.00,
            entity=self.entity,
            unit=self.unit
        )

    def test_create_invoice(self):
        invoice = Invoice.objects.create(
            project=self.project,
            customer=self.customer,
            invoice_amount=1500.00,
            invoice_date=date.today(),
            entity=self.entity,
            unit=self.unit
        )
        invoice.full_clean()
        invoice.save()
        self.assertEqual(invoice.invoice_amount, 1500.00)
        self.assertTrue(invoice.pk)

    def test_invoice_without_customer(self):
        invoice = Invoice(
            project=self.project,
            invoice_amount=1500.00,
            invoice_date=date.today(),
            entity=self.entity,
            unit=self.unit
        )
        with self.assertRaises(ValidationError):
            invoice.full_clean()

    def test_invoice_str_representation(self):
        invoice = Invoice.objects.create(
            project=self.project,
            customer=self.customer,
            invoice_amount=2000.00,
            invoice_date=date.today(),
            entity=self.entity,
            unit=self.unit
        )
        expected_str = f"Invoice {invoice.invoice_id}: {invoice.invoice_amount}"
        self.assertEqual(str(invoice), expected_str)
