from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import Entity, Unit
from hub.models import Customer, Contact
from hub.serializers import ContactSerializer
from rest_framework.test import APIRequestFactory

User = get_user_model()

class ContactSerializerTest(TestCase):
    def setUp(self):
        # Set up user, entity, unit, and customer
        self.user = User.objects.create(username="testuser")
        self.entity = Entity.objects.create(
            name="TestEnt",
            entity_type="SEC",
            description="EntityDesc"
        )
        self.unit = Unit.objects.create(
            name="Branch",
            unit_type="BR",
            entity=self.entity
        )
        self.customer = Customer.objects.create(
            customer_name="Test Customer",
            customer_email="testcustomer@example.com",
            customer_phone="1234567890",
            customer_address="123 Test Street",
            entity=self.entity,
            unit=self.unit
        )

        # Create an APIRequestFactory instance for creating mock requests
        self.factory = APIRequestFactory()

    def test_invalid_customer_reference(self):
        """Test for invalid customer reference in ContactSerializer."""
        data = {
            "contact_name": "John Doe",
            "contact_email": "johndoe@example.com",
            "contact_phone": "0987654321",
            "customer": 9999  # Non-existent ID
        }
        serializer = ContactSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("customer", serializer.errors)

    def test_missing_required_fields(self):
        """Test serializer with missing required fields."""
        data = {}  # Missing all fields
        serializer = ContactSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("contact_name", serializer.errors)
        self.assertIn("contact_email", serializer.errors)
        self.assertIn("customer", serializer.errors)

    def test_valid_contact_creation(self):
        """Test valid creation of a contact."""
        data = {
            "contact_name": "Jane Doe",
            "contact_email": "janedoe@example.com",
            "contact_phone": "0123456789",
            "customer": self.customer.pk
        }
        # Create a mock request and assign the user to it
        request = self.factory.post('/fake-url/')
        request.user = self.user

        # Pass the request context to the serializer
        serializer = ContactSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid())
        contact = serializer.save()
        
        # Assertions for saved contact
        self.assertEqual(contact.contact_name, "Jane Doe")
        self.assertEqual(contact.customer, self.customer)
        self.assertEqual(contact.created_by, self.user)
