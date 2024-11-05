# hub/tests/test_models/test_sales_model.py
from django.test import TestCase
from core.models import Entity, Unit, User, Employee, Instance
from hub.models import Customer, Sales
from django.core.exceptions import ValidationError
from datetime import date

class SalesModelTest(TestCase):
    def setUp(self):
        # Setting up the instance required for Employee model
        self.instance = Instance.objects.create(
            name="Instance Sales",
            code="INST01",
            industry="Tech"
        )

        # Setting up related entities
        self.entity = Entity.objects.create(
            name="Entity Sales",
            entity_type="SEC",
            description="Sales Entity",
            instance=self.instance
        )
        self.unit = Unit.objects.create(name="Unit Sales", unit_type="BR", entity=self.entity)
        
        # Setting up a user and employee
        self.user = User.objects.create_user(email="manager@example.com", password="password")
        self.employee = Employee.objects.create(
            user=self.user,
            entity=self.entity,
            unit=self.unit,
            instance=self.instance  # Adding the required instance field
        )
        
        # Setting up a customer
        self.customer = Customer.objects.create(
            customer_name="Sales Customer",
            customer_email="salescustomer@example.com",
            entity=self.entity,
            unit=self.unit
        )

    def test_create_sales(self):
        # Basic creation of Sales instance with essential fields
        sales = Sales.objects.create(
            sales_name="Project Alpha",
            customer=self.customer,
            sales_description="Description of project alpha",
            project_value=10000.00,
            expected_order_date=date(2024, 12, 1),
            sales_status="LEAD",
            project_manager=self.employee,
            created_by=self.user,
            entity=self.entity,
            unit=self.unit
        )
        self.assertEqual(sales.sales_name, "Project Alpha")
        self.assertEqual(sales.project_value, 10000.00)
        self.assertEqual(sales.sales_status, "LEAD")
        self.assertEqual(sales.project_manager, self.employee)

    def test_sales_status_choices(self):
        # Test invalid sales_status value raises ValidationError
        sales = Sales(
            sales_name="Invalid Status Sales",
            customer=self.customer,
            sales_description="Testing invalid status",
            project_value=5000.00,
            expected_order_date=date(2024, 12, 1),
            sales_status="INVALID_STATUS",  # Invalid choice
            entity=self.entity,
            unit=self.unit,
        )
        with self.assertRaises(ValidationError):
            sales.full_clean()  # Validate choices

    def test_sales_str(self):
        # Testing string representation
        sales = Sales.objects.create(
            sales_name="Project Beta",
            customer=self.customer,
            project_value=15000.00,
            expected_order_date=date(2025, 5, 1),
            entity=self.entity,
            unit=self.unit
        )
        self.assertEqual(str(sales), f"Sales {sales.sales_id}: Project Beta")
