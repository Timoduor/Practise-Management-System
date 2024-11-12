from django.test import TestCase
from core.models.entity import Entity
from core.models.unit import Unit
from core.models.user import User
from core.models.employee import Employee
from core.models.instance import Instance
from hub.models.customer import Customer
from hub.models.project import Project
from hub.models.project_phase import ProjectPhase
from hub.models.task import Task
from hub.models.task_status import TaskStatus
from datetime import date


class TaskModelTest(TestCase):
    def setUp(self):
        # Set up required instance, entity, unit, user, employee, customer, project, and project phase
        self.instance = Instance.objects.create(
            name="Instance for Tasks",
            code="INST04",
            industry="Education"
        )
        
        self.entity = Entity.objects.create(
            name="Entity for Tasks",
            entity_type="HC",
            description="Holding Entity for Tasks",
            instance=self.instance
        )
        
        self.unit = Unit.objects.create(name="Unit Tasks", unit_type="DEP", entity=self.entity)
        self.user = User.objects.create_user(email="task_manager@example.com", password="password")
        self.employee = Employee.objects.create(
            user=self.user,
            entity=self.entity,
            unit=self.unit,
            instance=self.instance
        )
        
        # Customer and project setup
        self.customer = Customer.objects.create(
            customer_name="Customer Tasks",
            customer_email="customertasks@example.com",
            entity=self.entity,
            unit=self.unit
        )
        
        self.project = Project.objects.create(
            project_name="Task Project",
            customer=self.customer,
            project_value=75000.00,
            start_date=date(2024, 4, 1),
            project_manager=self.employee,
            entity=self.entity,
            unit=self.unit
        )
        
        self.phase = ProjectPhase.objects.create(
            phase_name="Development Phase",
            project=self.project,
            start_date=date(2024, 5, 1)
        )

        # Create a TaskStatus instance for use in tests
        self.task_status = TaskStatus.objects.create(
            name="In Progress",
            description="Task is currently being worked on"
        )

    def test_create_task(self):
        # Create a Task instance and verify attributes
        task = Task.objects.create(
            task_name="Initial Setup",
            project=self.project,
            phase=self.phase,
            assigned_to=self.employee,
            task_description="Set up initial development environment",
            start_date=date(2024, 5, 2),
            due_date=date(2024, 5, 10),
            task_status=self.task_status  # Updated to use task_status instance
        )
        self.assertEqual(task.task_name, "Initial Setup")
        self.assertEqual(task.project, self.project)
        self.assertEqual(task.phase, self.phase)
        self.assertEqual(task.task_status, self.task_status)

    def test_task_ordering(self):
        # Test ordering by due_date
        task1 = Task.objects.create(
            task_name="Phase Documentation",
            project=self.project,
            phase=self.phase,
            due_date=date(2024, 5, 15),
            task_status=self.task_status
        )
        task2 = Task.objects.create(
            task_name="Code Review",
            project=self.project,
            phase=self.phase,
            due_date=date(2024, 5, 5),
            task_status=self.task_status
        )
        tasks = list(Task.objects.all())
        self.assertEqual(tasks[0], task2)
        self.assertEqual(tasks[1], task1)

    def test_task_str(self):
        # Testing string representation of Task
        task = Task.objects.create(
            task_name="Testing",
            project=self.project,
            phase=self.phase,
            due_date=date(2024, 5, 12),
            task_status=self.task_status
        )
        self.assertEqual(str(task), f"Testing in {self.phase.phase_name}")
