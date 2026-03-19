from django.core.exceptions import ValidationError  
from django.test import TestCase
from hub.models.contact import Contact
from hub.models.customer import Customer

class ContactModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            customer_name="Test Customer",
            customer_email="customer@example.com"
        )

    def test_create_contact_with_required_fields(self):
        contact = Contact.objects.create(
            customer=self.customer,
            contact_name="Jane Doe",
            contact_email="jane.doe@example.com"
        )
        contact.full_clean()  # Validate fields
        self.assertIsNotNone(contact.pk)
        self.assertEqual(contact.contact_name, "Jane Doe")
        self.assertEqual(contact.contact_email, "jane.doe@example.com")

    def test_create_contact_with_all_fields(self):
        contact = Contact.objects.create(
            customer=self.customer,
            contact_name="John Smith",
            contact_email="john.smith@example.com",
            contact_phone="+123456789",
            contact_address="123 Main Street, Cityville",
            contact_role="Manager"
        )
        contact.full_clean()
        contact.save()
        self.assertIsNotNone(contact.pk)
        self.assertEqual(contact.contact_role, "Manager")
        self.assertEqual(contact.contact_phone, "+123456789")
        self.assertEqual(contact.contact_address, "123 Main Street, Cityville")

    def test_contact_without_customer(self):
        contact = Contact(
            contact_name="Emily Taylor",
            contact_email="emily.taylor@example.com"
        )
        with self.assertRaises(ValidationError):
            contact.full_clean()

    def test_contact_str_representation(self):
        contact = Contact.objects.create(
            customer=self.customer,
            contact_name="Alice Johnson",
            contact_email="alice.johnson@example.com"
        )
        self.assertEqual(str(contact), f"{contact.contact_name} - {contact.contact_role or 'No Role'} ({self.customer})")
