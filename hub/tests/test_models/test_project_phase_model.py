# hub/tests/test_models/test_project_phase_model.py
from django.test import TestCase
from core.models.entity import Entity
from core.models.unit import Unit
from core.models.entity_type import EntityType
from core.models.unit_type import UnitType
from core.models.user import User
from core.models.employee import Employee
from core.models.instance import Instance
from hub.models.customer import Customer
from hub.models.project import Project
from hub.models.project_phase import ProjectPhase
from datetime import date

class ProjectPhaseModelTest(TestCase):
    def setUp(self):
        # Setting up required instance and related objects
        self.instance = Instance.objects.create(
            name="Instance for Phases",
            code="INST03",
            industry="Technology"
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
        self.user = User.objects.create_user(email="manager_phases@example.com", password="password")
        self.employee = Employee.objects.create(
            user=self.user,
            entity=self.entity,
            unit=self.unit,
            instance=self.instance
        )
        
        # Setting up a customer and project
        self.customer = Customer.objects.create(
            customer_name="Customer Phases",
            customer_email="customerphases@example.com",
            entity=self.entity,
            unit=self.unit
        )
        
        self.project = Project.objects.create(
            project_name="Phase Project",
            customer=self.customer,
            project_value=50000.00,
            start_date=date(2024, 1, 1),
            project_manager=self.employee,
            entity=self.entity,
            unit=self.unit
        )

    def test_create_project_phase(self):
        # Create a ProjectPhase instance and verify basic attributes
        phase = ProjectPhase.objects.create(
            phase_name="Design Phase",
            project=self.project,
            phase_description="Initial design phase",
            start_date=date(2024, 1, 10),
            end_date=date(2024, 2, 10)
        )
        self.assertEqual(phase.phase_name, "Design Phase")
        self.assertEqual(phase.project, self.project)
        self.assertEqual(phase.phase_description, "Initial design phase")

    def test_project_phase_ordering(self):
        # Test ordering by start_date
        phase1 = ProjectPhase.objects.create(
            phase_name="Phase One",
            project=self.project,
            start_date=date(2024, 3, 1)
        )
        phase2 = ProjectPhase.objects.create(
            phase_name="Phase Two",
            project=self.project,
            start_date=date(2024, 2, 1)
        )
        phases = list(ProjectPhase.objects.all())
        self.assertEqual(phases[0], phase2)
        self.assertEqual(phases[1], phase1)

    def test_project_phase_str(self):
        # Testing string representation of ProjectPhase
        phase = ProjectPhase.objects.create(
            phase_name="Execution Phase",
            project=self.project,
            start_date=date(2024, 3, 10)
        )
        self.assertEqual(str(phase), f"Phase: Execution Phase of {self.project.project_name}")
