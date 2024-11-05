from django.test import TestCase
from hub.models import WorkEntries, Customer, Project, ProjectPhase, Task, Sales, SalesTask
from core.models import User, Entity, Unit, Employee, Instance
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError

class WorkEntriesModelTest(TestCase):
    def setUp(self):
        # Set up required models with appropriate field lengths
        self.instance = Instance.objects.create(name="TestInst", code="TST", industry="Tech")

        self.entity = Entity.objects.create(
            name="TestEntity",
            entity_type="SEC",
            instance=self.instance
        )

        self.unit = Unit.objects.create(
            name="Unit1",
            entity=self.entity,
            unit_type="BR"
        )

        self.user = User.objects.create_user(
            email="user@example.com", 
            password="password123", 
            first_name="First", 
            last_name="Last"
        )

        self.employee = Employee.objects.create(
            user=self.user, 
            entity=self.entity, 
            unit=self.unit, 
            instance=self.instance
        )

        # Related objects for WorkEntries
        self.customer = Customer.objects.create(
            customer_name="TestCustomer", 
            customer_email="customer@example.com", 
            entity=self.entity, 
            unit=self.unit
        )

        self.project = Project.objects.create(
            project_name="TestProject",
            customer=self.customer,
            entity=self.entity,
            unit=self.unit,
            project_value=50000.00
        )

        self.phase = ProjectPhase.objects.create(
            phase_name="Phase1",
            project=self.project
        )

        self.task = Task.objects.create(
            task_name="Task1",
            project=self.project,
            phase=self.phase
        )

        self.sales = Sales.objects.create(
            sales_name="TestSales",
            customer=self.customer,
            project_value=10000.00,
            expected_order_date=datetime.today().date(),
            entity=self.entity,
            unit=self.unit
        )

        self.sales_task = SalesTask.objects.create(
            task_name="SalesTask1",
            sale=self.sales
        )

    def test_create_work_entry(self):
        work_entry = WorkEntries(
            user=self.user,
            date=datetime.today().date(),
            start_time=datetime.now().time(),
            end_time=(datetime.now() + timedelta(hours=1)).time(),
            description="Work entry description",
            customer=self.customer,
            project=self.project,
            phase=self.phase,
            task=self.task
        )
        # Trigger model validations before saving
        work_entry.full_clean()
        work_entry.save()

        self.assertIsNotNone(work_entry.pk)
        self.assertEqual(work_entry.user, self.user)
        self.assertEqual(work_entry.customer, self.customer)
        self.assertEqual(work_entry.description, "Work entry description")

    def test_duration_calculation(self):
        start_time = datetime.now().time()
        end_time = (datetime.now() + timedelta(hours=2)).time()
        work_entry = WorkEntries(
            user=self.user,
            date=datetime.today().date(),
            start_time=start_time,
            end_time=end_time,
            customer=self.customer
        )
        work_entry.full_clean()
        work_entry.save()

        self.assertEqual(work_entry.duration, timedelta(hours=2))

    def test_invalid_work_entry_combinations(self):
        work_entry = WorkEntries(
            user=self.user,
            date=datetime.today().date(),
            start_time=datetime.now().time(),
            end_time=(datetime.now() + timedelta(hours=1)).time(),
            project=self.project,
            sales_task=self.sales_task
        )

        # Check that ValidationError is raised for invalid combination
        with self.assertRaises(ValidationError) as e:
            work_entry.full_clean()

        self.assertIn("A WorkEntry can relate to either a Project/Task or Sale/SalesTask, but not both.", str(e.exception))

    def test_work_entry_str_representation(self):
        work_entry = WorkEntries(
            user=self.user,
            date=datetime.today().date(),
            start_time=datetime.now().time(),
            end_time=(datetime.now() + timedelta(hours=1)).time(),
            project=self.project,
            phase=self.phase,
            task=self.task,
            description="Example Work Entry"
        )
        work_entry.full_clean()
        work_entry.save()

        self.assertEqual(str(work_entry), f"Work entry on {self.project} - {self.phase} - {self.task}")
