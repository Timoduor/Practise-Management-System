# hub/tests/test_models/test_sales_model.py
from django.test import TestCase
from core.models.entity import Entity
from core.models.unit import Unit
from core.models.user import User
from core.models.employee import Employee
from core.models.instance import Instance
from core.models.entity_type import EntityType
from core.models.unit_type import UnitType
from hub.models.customer import Customer
from hub.models.sales import Sales
from hub.models.sales_type import SalesType
from datetime import date

class SalesModelTest(TestCase):
    def setUp(self):
        # Setting up instance required for Employee model
        self.instance = Instance.objects.create(
            name="Instance Sales",
            code="INST01",
            industry="Tech"
        )

        # Setting up related entities
        self.entity_type = EntityType.objects.create(name="SEC", description="Consists of a single entity")
        self.entity = Entity.objects.create(
            name="Entity Project",
            entity_type=self.entity_type,
            description="Holding Company for Project",
            instance=self.instance
        )
        
        self.unit_type = UnitType.objects.create(name="Branch", description="Location based")
        self.unit = Unit.objects.create(name="UnitName", unit_type=self.unit_type, entity=self.entity)
        
        
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

        # Setting up a SalesType instance for sales_status
        self.sales_type = SalesType.objects.create(name="LEAD", description="Lead status")

    def test_create_sales(self):
        # Basic creation of Sales instance with essential fields
        sales = Sales.objects.create(
            sales_name="Project Alpha",
            customer=self.customer,
            sales_description="Description of project alpha",
            project_value=10000.00,
            expected_order_date=date(2024, 12, 1),
            sales_status=self.sales_type,  # Set a valid SalesType instance
            project_manager=self.employee,
            created_by=self.user,
            entity=self.entity,
            unit=self.unit
        )
        self.assertEqual(sales.sales_name, "Project Alpha")
        self.assertEqual(sales.project_value, 10000.00)
        self.assertEqual(sales.sales_status, self.sales_type)
        self.assertEqual(sales.project_manager, self.employee)

    def test_sales_status_type(self):
        # Create a sales record without assigning a SalesType
        sales = Sales.objects.create(
            sales_name="Project Without SalesType",
            customer=self.customer,
            project_value=8000.00,
            expected_order_date=date(2024, 12, 1),
            project_manager=self.employee,
            created_by=self.user,
            entity=self.entity,
            unit=self.unit
        )
        # Assert that the Sales instance is created successfully without sales_status
        self.assertIsNotNone(sales.pk)
        self.assertIsNone(sales.sales_status)

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
