# hub/tests/test_models/test_sales_task_type_model.py

from django.test import TestCase
from hub.models.sales_task_type import SalesTaskType
from django.core.exceptions import ValidationError


class SalesTaskTypeModelTest(TestCase):

    def test_create_sales_task_type(self):
        # Test creating a SalesTaskType instance
        task_type = SalesTaskType.objects.create(
            name="Consultation",
            description="Consultation with the client about the product"
        )
        self.assertEqual(task_type.name, "Consultation")
        self.assertEqual(task_type.description, "Consultation with the client about the product")
        self.assertIsNotNone(task_type.pk)  # Ensure the object is saved

    def test_name_uniqueness(self):
        # Create a SalesTaskType instance
        SalesTaskType.objects.create(name="Meeting", description="Team meeting to discuss project")
        
        # Attempt to create another with the same name, expecting a ValidationError
        duplicate_task_type = SalesTaskType(name="Meeting", description="Another task with the same type")
        with self.assertRaises(ValidationError):
            duplicate_task_type.full_clean()  # full_clean will trigger validation

    def test_str_representation(self):
        # Test string representation of SalesTaskType
        task_type = SalesTaskType.objects.create(
            name="Follow-Up",
            description="Follow-up with client post-sales"
        )
        self.assertEqual(str(task_type), "Follow-Up")
