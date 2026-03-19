# hub/tests/test_views/test_common_viewset.py

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from unittest.mock import patch
from hub.models import Customer, Employee, Entity, Unit  # Include any other necessary models
from hub.serializers import CustomerSerializer

User = get_user_model()

class CommonViewSetTests(APITestCase):
    def setUp(self):
        # Create a user and authenticate
        self.user = User.objects.create_user(email="testuser@example.com", password="password")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Create required related objects for Employee with shortened names
        self.entity = Entity.objects.create(name="Entity")
        self.unit = Unit.objects.create(name="Unit")
        # Assuming there is an instance relation in the Employee or Entity structure
        self.instance = self.entity.instance_set.create(name="Inst")  # Name under 15 characters

        # Create an Employee instance with required fields
        self.employee = Employee.objects.create(
            user=self.user,
            entity=self.entity,
            unit=self.unit,
            instance=self.instance  # Other required fields should follow
        )

        # Set up URL for the Customer view we're testing
        self.url = reverse("customer-list")  # Adjust if the Customer uses CommonViewSet

    @patch("hub.views.CustomerSerializer", CustomerSerializer)
    def test_create_view(self):
        # Define data for creating a Customer instance
        data = {
            "customer_name": "Cust1",
            "customer_email": "cust1@example.com",
            "customer_phone": "1234567890",
            "customer_address": "123 St"
        }

        # Send a POST request to create a new customer
        response = self.client.post(self.url, data, format="json")
        
        # Verify response status and data
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["customer_name"], "Cust1")
        self.assertEqual(response.data["customer_email"], "cust1@example.com")
        self.assertEqual(response.data["created_by_id"], self.user.id)
        self.assertEqual(response.data["last_updated_by_id"], self.user.id)

    @patch("hub.views.CustomerSerializer", CustomerSerializer)
    def test_update_view(self):
        # Create a customer instance first
        customer = Customer.objects.create(
            customer_name="Cust1",
            customer_email="cust1@example.com",
            customer_phone="0987654321",
            customer_address="456 St",
            created_by_id=self.user.id,
            last_updated_by_id=self.user.id
        )
        
        # Define the update URL and update data
        update_url = reverse("customer-detail", args=[customer.pk])
        update_data = {
            "customer_name": "UpdatedCust",
            "customer_phone": "1122334455",
            "customer_address": "789 Ave"
        }

        # Send a PATCH request to update the customer
        response = self.client.patch(update_url, update_data, format="json")
        
        # Verify response status and updated data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["customer_name"], "UpdatedCust")
        self.assertEqual(response.data["customer_phone"], "1122334455")
        self.assertEqual(response.data["customer_address"], "789 Ave")
        self.assertEqual(response.data["last_updated_by_id"], self.user.id)
