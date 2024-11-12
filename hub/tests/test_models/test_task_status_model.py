from django.test import TestCase
from hub.models.task_status import TaskStatus

class TaskStatusModelTest(TestCase):
    def setUp(self):
        # Create an initial TaskStatus instance
        self.task_status = TaskStatus.objects.create(
            name="In Progress",
            description="Task is currently being worked on"
        )

    def test_create_task_status(self):
        # Ensure TaskStatus instance was created successfully
        task_status = TaskStatus.objects.create(
            name="Completed",
            description="Task is finished"
        )
        self.assertEqual(task_status.name, "Completed")
        self.assertEqual(task_status.description, "Task is finished")
        self.assertEqual(TaskStatus.objects.count(), 2)  # One in setUp and one here

    def test_unique_name_constraint(self):
        # Test that creating a TaskStatus with duplicate name raises IntegrityError
        with self.assertRaises(Exception):  # Adjust to `IntegrityError` if needed
            TaskStatus.objects.create(name="In Progress")

    def test_ordering_by_name(self):
        # Create an additional TaskStatus with a name that comes alphabetically after "In Progress"
        TaskStatus.objects.create(name="Pending", description="Task is pending")
        statuses = list(TaskStatus.objects.all())
        self.assertEqual(statuses[0].name, "In Progress")
        self.assertEqual(statuses[1].name, "Pending")

    def test_str_representation(self):
        # Test the string representation
        self.assertEqual(str(self.task_status), "In Progress")
