from django.test import TestCase
from django.core.exceptions import ValidationError
from hub.models import LeaveType

class LeaveTypeModelTest(TestCase):

    def test_create_leave_type(self):
        """Test creating a LeaveType instance"""
        leave_type = LeaveType.objects.create(
            name="Annual Leave",
            description="Leave for annual vacation",
            is_paid=True
        )
        self.assertIsNotNone(leave_type.pk)
        self.assertEqual(leave_type.name, "Annual Leave")
        self.assertTrue(leave_type.is_paid)

    def test_leave_type_str_representation(self):
        """Test LeaveType string representation"""
        leave_type = LeaveType.objects.create(
            name="Sick Leave",
            description="Leave for illness",
            is_paid=False
        )
        self.assertEqual(str(leave_type), "Sick Leave")

    def test_leave_type_with_missing_fields(self):
        """Test LeaveType validation for missing required fields"""
        # Attempt to create a LeaveType without the required 'name' field
        leave_type = LeaveType(description="Emergency leave for personal issues", is_paid=False)
        
        with self.assertRaises(ValidationError):
            leave_type.full_clean()  # This should raise ValidationError due to missing 'name'
