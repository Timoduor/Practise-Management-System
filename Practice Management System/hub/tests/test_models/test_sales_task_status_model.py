# hub/tests/test_models/test_sales_task_status_model.py

from django.test import TestCase
from hub.models.sales_task_status import SalesTaskStatus
from django.core.exceptions import ValidationError


class SalesTaskStatusModelTest(TestCase):

    def test_create_sales_task_status(self):
        # Test creating a SalesTaskStatus instance
        status = SalesTaskStatus.objects.create(
            name="In Progress",
            description="The sales task is currently being worked on"
        )
        self.assertEqual(status.name, "In Progress")
        self.assertEqual(status.description, "The sales task is currently being worked on")
        self.assertIsNotNone(status.pk)  # Ensure the object is saved

    def test_name_uniqueness(self):
        # Create a SalesTaskStatus instance
        SalesTaskStatus.objects.create(name="Pending", description="Task is pending")
        
        # Attempt to create another with the same name, expecting a ValidationError
        duplicate_status = SalesTaskStatus(name="Pending", description="Another task with the same status")
        with self.assertRaises(ValidationError):
            duplicate_status.full_clean()  # full_clean will trigger validation

    def test_str_representation(self):
        # Test string representation of SalesTaskStatus
        status = SalesTaskStatus.objects.create(
            name="Completed",
            description="The task has been completed successfully"
        )
        self.assertEqual(str(status), "Completed")
