from django.test import TestCase
from core.models.entity import Entity
from core.models.unit import Unit
from hub.models.customer import Customer
from django.core.exceptions import ValidationError

class CustomerModelTest(TestCase):
    def setUp(self):
        # Adjust name lengths based on Entity model constraints
        self.entity = Entity.objects.create(name="EntityName", entity_type="SEC", description="Test Entity Description")
        self.unit = Unit.objects.create(name="UnitName", unit_type="BR", entity=self.entity)

    def test_create_customer(self):
        # Test valid creation of a customer with all fields
        customer = Customer.objects.create(
            customer_name="Test Customer",
            customer_email="testcustomer@example.com",
            customer_phone="1234567890",
            customer_address="123 Test Street, Test City",
            entity=self.entity,
            unit=self.unit,
        )
        self.assertEqual(customer.customer_name, "Test Customer")
        self.assertEqual(customer.customer_email, "testcustomer@example.com")
        self.assertEqual(customer.customer_phone, "1234567890")
        self.assertEqual(customer.customer_address, "123 Test Street, Test City")

    def test_customer_email_unique(self):
        # Ensure unique constraint on customer_email is enforced
        Customer.objects.create(
            customer_name="Unique Email Customer",
            customer_email="unique@example.com",
            entity=self.entity,
            unit=self.unit,
        )
        with self.assertRaises(ValidationError):
            duplicate_customer = Customer(
                customer_name="Duplicate Email Customer",
                customer_email="unique@example.com",
                entity=self.entity,
                unit=self.unit,
            )
            duplicate_customer.full_clean()  # Call full_clean to check for unique validation

    def test_optional_fields(self):
        # Verify creation with optional fields left blank
        customer = Customer.objects.create(
            customer_name="Optional Fields Customer",
            customer_email="optional@example.com"
        )
        self.assertEqual(customer.customer_phone, None)
        self.assertEqual(customer.customer_address, None)
        self.assertEqual(customer.entity, None)
        self.assertEqual(customer.unit, None)

    def test_customer_str(self):
        # Check string representation method
        customer = Customer.objects.create(
            customer_name="String Representation Customer",
            customer_email="string@example.com",
            entity=self.entity,
            unit=self.unit,
        )
        self.assertEqual(str(customer), "String Representation Customer")
