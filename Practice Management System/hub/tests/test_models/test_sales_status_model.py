# hub/tests/test_models/test_sales_status_model.py
from django.test import TestCase
from hub.models.sales_status import SalesStatus
from django.core.exceptions import ValidationError

class SalesStatusModelTest(TestCase):
    def setUp(self):
        # Set up a valid SalesStatus instance for testing
        self.sales_s = SalesStatus.objects.create(
            name="New Lead",
            description="A new lead in the sales funnel."
        )

    def test_sales_status_creation(self):
        # Ensure the sales_status instance was created successfully
        self.assertIsNotNone(self.sales_status.pk)
        self.assertEqual(self.sales_status.name, "New Lead")
        self.assertEqual(self.sales_status.description, "A new lead in the sales funnel.")

    def test_sales_status_name_uniqueness(self):
        # Test that duplicate names raise a ValidationError
        duplicate_sales_status = SalesStatus(name="New Lead")
        with self.assertRaises(ValidationError):
            duplicate_sales_status.full_clean()  # Validates uniqueness

    def test_sales_status_str_representation(self):
        # Test the string representation of SalesStatus
        self.assertEqual(str(self.sales_status), "New Lead")
