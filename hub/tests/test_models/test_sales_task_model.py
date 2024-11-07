from django.test import TestCase
from django.core.exceptions import ValidationError
from hub.models import SalesTask, Sales, Customer
from core.models import Entity, Unit, User, Employee, Instance


class SalesTaskModelTest(TestCase):

    def setUp(self):
        # Setup related models
        self.instance = Instance.objects.create(name="Test Instance", code="TI", industry="IT")
        self.entity = Entity.objects.create(
            name="Test Entity", 
            entity_type="SEC", 
            description="Test Description", 
            instance=self.instance
        )
        self.unit = Unit.objects.create(name="Headquarters", unit_type="DEP", entity=self.entity)
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
            expected_order_date="2024-06-10",
            created_by=self.user,
            entity=self.entity,
            unit=self.unit
        )

    def test_create_sales_task(self):
        sales_task = SalesTask.objects.create(
            task_name="Initial Meeting",
            sale=self.sale,
            task_type="MEETING",
            task_status="IN_PROGRESS",
            date="2024-06-12"
        )
        self.assertEqual(sales_task.task_name, "Initial Meeting")
        self.assertEqual(sales_task.task_type, "MEETING")
        self.assertEqual(sales_task.task_status, "IN_PROGRESS")
        self.assertEqual(sales_task.sale, self.sale)

    def test_sales_task_str(self):
        sales_task = SalesTask.objects.create(
            task_name="Follow-up Call",
            sale=self.sale,
            task_type="CALL",
            task_status="PENDING",
            date="2024-06-15"
        )
        self.assertEqual(str(sales_task), f"Follow-up Call in {self.sale.sales_name}")

    def test_sales_task_choices(self):
        # Test valid choices for task_type and task_status
        sales_task = SalesTask.objects.create(
            task_name="Initial Meeting",
            sale=self.sale,
            task_type="MEETING",
            task_status="IN_PROGRESS",
            date="2024-06-12"
        )
        self.assertEqual(sales_task.task_type, "MEETING")
        self.assertEqual(sales_task.task_status, "IN_PROGRESS")
        
        # Test invalid choices for task_type
        invalid_task = SalesTask(
            task_name="Invalid Task",
            sale=self.sale,
            task_type="INVALID_TYPE",  # Invalid task_type
            task_status="PENDING"
        )
        with self.assertRaises(ValidationError):
            invalid_task.full_clean()  # full_clean() triggers validation for choices
        
        # Test invalid choices for task_status
        invalid_status = SalesTask(
            task_name="Invalid Task Status",
            sale=self.sale,
            task_type="TO_DO",
            task_status="INVALID_STATUS"  # Invalid task_status
        )
        with self.assertRaises(ValidationError):
            invalid_status.full_clean()  # full_clean() triggers validation for choices
