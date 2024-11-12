from django.test import TestCase
from hub.models.work_entries import WorkEntries
from hub.models.customer import Customer
from hub.models.project import Project
from hub.models.project_phase import ProjectPhase
from hub.models.task import Task
from hub.models.task_type import TaskType
from core.models.user import User
from core.models.unit import Unit
from core.models.entity import Entity
from core.models.instance import Instance
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError



class WorkEntriesModelTest(TestCase):
    def setUp(self):
        self.instance = Instance.objects.create(name="TestInst", code="TST", industry="Tech")
        self.entity = Entity.objects.create(name="TestEntity", entity_type="SEC", instance=self.instance)
        self.unit = Unit.objects.create(name="Unit1", entity=self.entity, unit_type="BR")
        self.user = User.objects.create_user(email="user@example.com", password="password123")
        self.customer = Customer.objects.create(customer_name="TestCustomer", customer_email="customer@example.com")
        self.project = Project.objects.create(project_name="TestProject", customer=self.customer, project_value=50000.00)
        self.phase = ProjectPhase.objects.create(phase_name="Phase1", project=self.project)
        self.task = Task.objects.create(task_name="Task1", project=self.project, phase=self.phase)
        self.task_type = TaskType.objects.create(name="Development", description="Development tasks")

    def test_create_work_entry_with_task_type(self):
        work_entry = WorkEntries(
            user=self.user,
            date=datetime.today().date(),
            start_time=datetime.now().time(),
            end_time=(datetime.now() + timedelta(hours=1)).time(),
            description="Work entry description",
            customer=self.customer,
            project=self.project,
            phase=self.phase,
            task=self.task,
            task_type=self.task_type
        )
        work_entry.full_clean()  # Ensures validation checks are passed
        work_entry.save()

        self.assertIsNotNone(work_entry.pk)
        self.assertEqual(work_entry.user, self.user)
        self.assertEqual(work_entry.customer, self.customer)
        self.assertEqual(work_entry.description, "Work entry description")
        self.assertEqual(work_entry.task_type, self.task_type)

    def test_duration_calculation(self):
        start_time = datetime.now().time()
        end_time = (datetime.now() + timedelta(hours=2)).time()
        work_entry = WorkEntries(
            user=self.user,
            date=datetime.today().date(),
            start_time=start_time,
            end_time=end_time,
            customer=self.customer,
            task_type=self.task_type
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
            task=self.task,
            description="Invalid entry"
        )

        # Check for validation error due to invalid combination
        with self.assertRaises(ValidationError) as e:
            work_entry.full_clean()

        self.assertIn("A Task must be associated with a Project.", str(e.exception))

    def test_task_without_project_raises_error(self):
        work_entry = WorkEntries(
            user=self.user,
            date=datetime.today().date(),
            start_time=datetime.now().time(),
            end_time=(datetime.now() + timedelta(hours=1)).time(),
            task=self.task,
            task_type=self.task_type
        )

        with self.assertRaises(ValidationError) as e:
            work_entry.full_clean()

        self.assertIn("A Task must be associated with a Project.", str(e.exception))

    def test_work_entry_str_representation(self):
        work_entry = WorkEntries(
            user=self.user,
            date=datetime.today().date(),
            start_time=datetime.now().time(),
            end_time=(datetime.now() + timedelta(hours=1)).time(),
            project=self.project,
            phase=self.phase,
            task=self.task,
            task_type=self.task_type,
            description="Example Work Entry"
        )
        work_entry.full_clean()
        work_entry.save()

        self.assertEqual(str(work_entry), f"Work entry on {self.project} - {self.phase} - {self.task}")
