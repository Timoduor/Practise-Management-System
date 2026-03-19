# hub/tests/test_models/test_project_model.py
from django.test import TestCase
from core.models.entity import Entity
from core.models.unit import Unit
from core.models.user import User
from core.models.employee import Employee
from core.models.instance import Instance
from core.models.entity_type import EntityType
from core.models.unit_type import UnitType
from hub.models.customer import Customer
from hub.models.project import Project
from datetime import date

class ProjectModelTest(TestCase):
    def setUp(self):
        # Setting up required instance and related objects
        self.instance = Instance.objects.create(
            name="Instance Project",
            code="INST02",
            industry="Finance"
        )
        
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
        self.user = User.objects.create_user(email="manager_project@example.com", password="password")
        self.employee = Employee.objects.create(
            user=self.user,
            entity=self.entity,
            unit=self.unit,
            instance=self.instance
        )
        
        # Setting up a customer
        self.customer = Customer.objects.create(
            customer_name="Project Customer",
            customer_email="projectcustomer@example.com",
            entity=self.entity,
            unit=self.unit
        )

    def test_create_project(self):
        # Create a project instance and verify basic attributes
        project = Project.objects.create(
            project_name="Alpha Project",
            customer=self.customer,
            project_description="Description for Alpha Project",
            project_value=20000.00,
            start_date=date(2024, 11, 15),
            end_date=date(2025, 1, 15),
            project_manager=self.employee,
            entity=self.entity,
            unit=self.unit
        )
        self.assertEqual(project.project_name, "Alpha Project")
        self.assertEqual(project.project_value, 20000.00)
        self.assertEqual(project.project_manager, self.employee)

    def test_project_ordering(self):
        # Test ordering by start_date
        project1 = Project.objects.create(
            project_name="First Project",
            customer=self.customer,
            project_value=5000.00,
            start_date=date(2024, 5, 1),
            entity=self.entity,
            unit=self.unit
        )
        project2 = Project.objects.create(
            project_name="Second Project",
            customer=self.customer,
            project_value=10000.00,
            start_date=date(2024, 1, 1),
            entity=self.entity,
            unit=self.unit
        )
        projects = list(Project.objects.all())
        self.assertEqual(projects[0], project2)
        self.assertEqual(projects[1], project1)

    def test_project_str(self):
        # Testing string representation of Project
        project = Project.objects.create(
            project_name="Beta Project",
            customer=self.customer,
            project_value=15000.00,
            start_date=date(2024, 12, 1),
            entity=self.entity,
            unit=self.unit
        )
        self.assertEqual(str(project), "Beta Project")
