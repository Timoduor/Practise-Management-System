from django.test import TestCase
from django.core.exceptions import ValidationError
from core.models.entity import Entity
from core.models.unit import Unit
from core.models.user import User
from core.models.employee import Employee
from core.models.instance import Instance
from core.models.entity_type import EntityType
from core.models.unit_type import UnitType
from hub.models.customer import Customer
from hub.models.sales import Sales
from hub.models.sales_task import SalesTask
from hub.models.sales_task_type import SalesTaskType
from hub.models.sales_task_status import SalesTaskStatus
from datetime import date


class SalesTaskModelTest(TestCase):

    def setUp(self):
        self.instance = Instance.objects.create(name="Test Instance", code="TI", industry="IT")
        self.entity_type = EntityType.objects.create(name="SEC", description="Consists of a single entity")
        self.entity = Entity.objects.create(
            name="Entity Project",
            entity_type=self.entity_type,
            description="Holding Company for Project",
            instance=self.instance
        )
        
        self.unit_type = UnitType.objects.create(name="Branch", description="Location based")
        self.unit = Unit.objects.create(name="UnitName", unit_type=self.unit_type, entity=self.entity)
        
        self.user = User.objects.create_user(email="testuser@example.com", password="password")
        self.customer = Customer.objects.create(
            customer_name="Test Customer",
            customer_email="customer@example.com",
            entity=self.entity,
            unit=self.unit
        )
        self.employee = Employee.objects.create(
            user=self.user, 
            entity=self.entity, 
            unit=self.unit, 
            instance=self.instance
        )
        self.sale = Sales.objects.create(
            sales_name="Test Sale",
            customer=self.customer,
            project_value=1000.00,
            expected_order_date=date(2024, 6, 10),
            created_by=self.user,
            entity=self.entity,
            unit=self.unit
        )

        # Set up task type and task status
        self.task_type = SalesTaskType.objects.create(name="Meeting", description="Initial meeting with the client")
        self.task_status = SalesTaskStatus.objects.create(name="In Progress", description="Task is currently active")

    def test_create_sales_task(self):
        sales_task = SalesTask.objects.create(
            task_name="Initial Meeting",
            sale=self.sale,
            task_type=self.task_type,
            task_status=self.task_status,
            assigned_to=self.employee,
            date=date(2024, 6, 12)
        )
        self.assertEqual(sales_task.task_name, "Initial Meeting")
        self.assertEqual(sales_task.task_type, self.task_type)
        self.assertEqual(sales_task.task_status, self.task_status)
        self.assertEqual(sales_task.sale, self.sale)
        self.assertEqual(sales_task.assigned_to, self.employee)

    def test_sales_task_str(self):
        sales_task = SalesTask.objects.create(
            task_name="Follow-up Call",
            sale=self.sale,
            task_type=self.task_type,
            task_status=self.task_status,
            date=date(2024, 6, 15)
        )
        self.assertEqual(str(sales_task), f"Follow-up Call in {self.sale.sales_name}")

    def test_invalid_task_type_and_status(self):
        # Test missing task_type
        invalid_task_type = SalesTask(
            task_name="Invalid Task",
            sale=self.sale,
            task_type=None,  # No task_type provided
            task_status=self.task_status
        )
        with self.assertRaises(ValidationError) as e:
            invalid_task_type.full_clean()
        self.assertIn("task_type", e.exception.message_dict)

        # Test missing task_status
        invalid_task_status = SalesTask(
            task_name="Invalid Status Task",
            sale=self.sale,
            task_type=self.task_type,
            task_status=None  # No task_status provided
        )
        with self.assertRaises(ValidationError) as e:
            invalid_task_status.full_clean()
        self.assertIn("task_status", e.exception.message_dict)
