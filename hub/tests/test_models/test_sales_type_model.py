# hub/tests/test_models/test_sales_type_model.py
from django.test import TestCase
from hub.models.sales_type import SalesType
from django.core.exceptions import ValidationError

class SalesTypeModelTest(TestCase):
    def setUp(self):
        # Set up a valid SalesType instance for testing
        self.sales_type = SalesType.objects.create(
            name="New Lead",
            description="A new lead in the sales funnel."
        )

    def test_sales_type_creation(self):
        # Ensure the sales_type instance was created successfully
        self.assertIsNotNone(self.sales_type.pk)
        self.assertEqual(self.sales_type.name, "New Lead")
        self.assertEqual(self.sales_type.description, "A new lead in the sales funnel.")

    def test_sales_type_name_uniqueness(self):
        # Test that duplicate names raise a ValidationError
        duplicate_sales_type = SalesType(name="New Lead")
        with self.assertRaises(ValidationError):
            duplicate_sales_type.full_clean()  # Validates uniqueness

    def test_sales_type_str_representation(self):
        # Test the string representation of SalesType
        self.assertEqual(str(self.sales_type), "New Lead")
