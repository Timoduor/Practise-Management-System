from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models.entity import Entity
from core.models.unit import Unit
from core.models.entity_type import EntityType
from core.models.unit_type import UnitType
from hub.models import Customer, Contact
from hub.serializers import ContactSerializer
from rest_framework.test import APIRequestFactory

User = get_user_model()

class ContactSerializerTest(TestCase):
    def setUp(self):
        # Check if the User model expects an email instead of username
        user_kwargs = {"email": "testuser@example.com"} if hasattr(User, 'email') else {"username": "testuser"}
        self.user = User.objects.create(**user_kwargs)

        # Set up other models as required
        self.entity_type = EntityType.objects.create(name="SEC", description="Consists of a single entity")
        self.entity = Entity.objects.create(
            name="Entity Project",
            entity_type=self.entity_type,
            description="Holding Company for Project",
            instance=self.instance
        )
        
        self.unit_type = UnitType.objects.create(name="Branch", description="Location based")
        self.unit = Unit.objects.create(name="UnitName", unit_type=self.unit_type, entity=self.entity)
        
        self.customer = Customer.objects.create(
            customer_name="Test Customer",
            customer_email="testcustomer@example.com",
            customer_phone="1234567890",
            customer_address="123 Test Street",
            entity=self.entity,
            unit=self.unit
        )

        # Mock request setup
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
        # Mock request with user
        request = self.factory.post('/fake-url/')
        request.user = self.user

        # Use serializer with request context
        serializer = ContactSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid())
        contact = serializer.save()
        
        # Assertions for saved contact
        self.assertEqual(contact.contact_name, "Jane Doe")
        self.assertEqual(contact.customer, self.customer)
        self.assertEqual(contact.created_by, self.user)
