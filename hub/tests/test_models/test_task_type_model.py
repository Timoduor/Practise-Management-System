from django.test import TestCase
from hub.models.task_type import TaskType
from django.db import IntegrityError

class TaskTypeModelTest(TestCase):
    
    def setUp(self):
        # Set up a basic TaskType instance for reuse
        self.task_type = TaskType.objects.create(
            name="Development",
            description="Tasks related to development activities."
        )

    def test_create_task_type(self):
        # Test creation and basic fields
        task_type = TaskType.objects.create(
            name="Testing",
            description="Tasks related to testing and quality assurance."
        )
        self.assertIsNotNone(task_type.pk)
        self.assertEqual(task_type.name, "Testing")
        self.assertEqual(task_type.description, "Tasks related to testing and quality assurance.")

    def test_task_type_name_unique(self):
        # Test that creating a TaskType with a duplicate name raises an IntegrityError
        with self.assertRaises(IntegrityError):
            TaskType.objects.create(
                name="Development",  # Duplicate name
                description="A duplicate task type."
            )

    def test_task_type_str_representation(self):
        # Test the string representation
        self.assertEqual(str(self.task_type), "Development")
